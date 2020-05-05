# -*- coding: utf-8 -*-
import sys

from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils import timezone

from ovp.apps.organizations.models import Organization
from ovp.apps.projects.models import Project


class Command(BaseCommand):
    help = "Reminder for organizations that do not \
            create projects for more than 3 months"

    def handle(self, *args, **options):
        today = timezone.now()
        start_date = today - timezone.timedelta(days=90)

        criterion1 = Q(created_date__range=(start_date, today))
        criterion2 = Q(closed=True)

        projects = Project \
            .objects \
            .values('organization', 'created_date') \
            .exclude(criterion1 | criterion2) \
            .distinct()

        for project in projects:
            try:
                organization = Organization.objects.get(
                    pk=project['organization'], published=True)
                if not organization.is_inactive:
                    limite = today - project['created_date']
                    organization.is_inactive = (limite.days > 365)

                    if organization.reminder_sent:
                        interval = today - organization.reminder_sent_date

                        if interval.days > 90:
                            organization.reminder_sent_date = today
                            organization.mailing().sendOrganizationReminder(
                                context={"organization": organization})
                    else:
                        organization.reminder_sent = True
                        organization.reminder_sent_date = today
                        organization.mailing().sendOrganizationReminder(
                            context={"organization": organization})

                    organization.save()
            except BaseException:
                pass
