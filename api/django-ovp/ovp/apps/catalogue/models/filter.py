from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.utils.translation import ugettext as _

from ovp.apps.channels.models.abstract import ChannelRelationship


class Filter(ChannelRelationship):
    """
    This base class can be extended to create custom catalogue filters.
    """

    def __str__(self):
        return "Base filter"

    class Meta:
        abstract = True

    def get_filter_kwargs(self):
        """
        This should return a dictionary. This dictionary will be passed as
        **kwargs to Project.filter() when building a catalogue.

        Unfortunately we cannot operate on the queryset directly as catalogues
        get cached for performance reasons and we can't pickle functions.
        """
        raise NotImplementedError(
            "You must override .get_filter_kwargs when \
            implementing your custom catalogue filter."
        )


###################
# Category Filter #
###################

class CategoryFilter(Filter):
    categories = models.ManyToManyField("projects.Category")

    def __str__(self):
        return _("Category Filter")

    def filter_information(self):
        categories_str = ""
        for category in self.categories.all():
            categories_str += "%s\n" % category.name
        return categories_str

    def get_filter_kwargs(self):
        pks = list(self.categories.all().values_list("pk", flat=True))
        return {"categories__pk__in": pks}


####################
# DateDelta Filter #
####################

DATEDELTA_OPERATORS = (
    ("exact", _("Exact")),
    ("gt", _("Greater than")),
    ("gte", _("Greater than or equal to")),
    ("lt", _("Lesser than")),
    ("lte", _("Lesser than or equal to")),
)


class DateDeltaFilter(Filter):
    days = models.IntegerField(_("Days"), default=0)
    weeks = models.IntegerField(_("Weeks"), default=0)
    months = models.IntegerField(_("Months"), default=0)
    years = models.IntegerField(_("Years"), default=0)
    operator = models.CharField(
        _("Operator"),
        choices=DATEDELTA_OPERATORS,
        default="exact",
        max_length=30
    )

    def __str__(self):
        return _("DateDelta Filter")

    def filter_information(self):
        result_str = "{} {} days, {} weeks, {} months, {} years".format(
            self.get_operator_display(),
            self.days,
            self.weeks,
            self.months,
            self.years
        )
        return result_str

    def get_filter_kwargs(self):
        k = "published_date__{}".format(self.operator)
        delta = relativedelta(
            days=self.days,
            weeks=self.weeks,
            months=self.months,
            years=self.years
        )
        v = timezone.now() + delta
        return {k: v}


####################
# Highlighted Filter #
####################

HIGHLIGHTED_OPTIONS = (
    (1, _("True")),
    (0, _("False")),
)


class HighlightedFilter(Filter):
    highlighted = models.IntegerField(
        _("Highlighted"),
        choices=HIGHLIGHTED_OPTIONS,
        default=1
    )

    def __str__(self):
        return _("Highlighted Filter")

    def filter_information(self):
        return "Highlighted: {}".format(self.get_highlighted_display())

    def get_filter_kwargs(self):
        return {"highlighted": self.highlighted}

##################
# Address Filter #
##################
COMPONENT_TYPE_CHOICES = (
    ('administrative_area_level_1', 'administrative_area_level_1'),
    ('administrative_area_level_2', 'administrative_area_level_2'),
    ('county', 'county'),
    ('locality', 'locality'),
    ('sublocality', 'sublocality'),
    ('country', 'country'),
)
class AddressFilter(Filter):
    filter_json = JSONField(
        _("Filter parameters"),
        null=True,
        blank=True
    )
    component_type = models.CharField(
        _("Component type"),
        choices=COMPONENT_TYPE_CHOICES,
        blank=True,
        null=True,
        max_length=100
    )
    name = models.CharField(
        _("Component name"),
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return _("Address filter")

    def filter_information(self):
        return "Address: {}".format(self.name)

    def get_filter_kwargs(self):
        if self.name and self.component_type:
            return {"address__address_components__long_name": self.name, "address__address_components__types__name": self.component_type}
        return self.filter_json
