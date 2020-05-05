import datetime
from django.utils import timezone
from django.utils.dateparse import parse_date
from dateutil.relativedelta import relativedelta
from jet.dashboard.modules import RecentActions
from jet.dashboard.modules import DashboardModule
from django.contrib.admin.models import LogEntry
from django.db.models import Q
from ovp.apps.organizations.models import Organization
from ovp.apps.projects.models import Project, Apply, VolunteerRole
from ovp.apps.users.models import User
from django.db.models import Sum
from django.conf import settings


class OVPRecentActions(RecentActions):
    def init_with_context(self, context):
        def get_qset(list):
            qset = None
            for contenttype in list:
                try:
                    app_label, model = contenttype.split('.')

                    if model == '*':
                        current_qset = Q(
                            content_type__app_label=app_label
                        )
                    else:
                        current_qset = Q(
                            content_type__app_label=app_label,
                            content_type__model=model
                        )
                except BaseException:
                    raise ValueError('Invalid contenttype: "%s"' % contenttype)

                if qset is None:
                    qset = current_qset
                else:
                    qset = qset | current_qset
            return qset

        qs = LogEntry.objects

        if self.user:
            qs = qs.filter(
                user__pk=int(self.user)
            )

        if self.include_list:
            qs = qs.filter(get_qset(self.include_list))
        if self.exclude_list:
            qs = qs.exclude(get_qset(self.exclude_list))

        qs = qs.filter(user__channel=context["user"].channel)

        self.children = qs.select_related('content_type', 'user')[
            :int(self.limit)]


class Indicators(DashboardModule):
    title = "Indicators"
    title_url = "#"
    template = "admin/indicators.html"

    def init_with_context(self, context):
        date_min = context["request"].GET.get("indicator__gte", None)
        date_max = context["request"].GET.get("indicator__lte", None)

        if date_min:
            date_min = parse_date(date_min)

        if date_max:
            date_max = parse_date(date_max)

        if date_min and date_max and date_max <= date_min:
            tmp = date_min
            date_min = date_max
            date_max = tmp

        channel = context["user"].channel
        organizations_created = self.date_filter(Organization.objects.filter(
            deleted=False, channel=channel), date_min, date_max, "created_date")
        organizations_published = self.date_filter(Organization.objects.filter(
            deleted=False, channel=channel), date_min, date_max, "published_date")
        projects_created = self.date_filter(
            Project.objects.filter(
                deleted=False,
                channel=channel),
            date_min,
            date_max,
            "created_date")
        projects_published = self.date_filter(
            Project.objects.filter(
                deleted=False,
                channel=channel),
            date_min,
            date_max,
            "published_date")
        projects_published_pks = list(
            projects_published.values_list(
                'pk', flat=True))
        users = self.date_filter(
            User.objects.filter(
                channel=channel),
            date_min,
            date_max,
            "joined_date")
        applies = self.date_filter(
            Apply.objects.filter(
                status__in=['confirmed-volunter', 'applied'],
                channel=channel),
            date_min,
            date_max,
            "date")

        apply_distinct_qs = Apply.objects.all()
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            apply_distinct_qs = apply_distinct_qs.distinct('user')
        applies_distinct = self.date_filter(
            apply_distinct_qs, date_min, date_max, "date")

        self.organizations_count = organizations_created.count()
        self.organizations_published_count = organizations_published.filter(
            published=True).count()
        self.projects_count = projects_created.count()
        self.projects_published_count = projects_published.filter(
            published=True).count()
        self.users_count = users.count()
        self.applies_count = applies.count()
        self.applies_count_distinct = applies_distinct.count()
        self.vacancies = VolunteerRole.objects.filter(
            project__pk__in=projects_published_pks).aggregate(
            Sum('vacancies'))['vacancies__sum']
        if not self.vacancies:
            self.vacancies = 0

        self.benefited_people_count = projects_published.aggregate(
            Sum('benefited_people'))["benefited_people__sum"]
        if not self.benefited_people_count:
            self.benefited_people_count = 0

        self.date_min = date_min
        self.date_max = date_max

    def date_filter(self, qs, date_min, date_max, field=None):
        filters = {}

        if date_min:
            filters["{}__gte".format(field)] = date_min

        if date_max:
            filters["{}__lte".format(field)] = date_max

        return qs.filter(**filters)
