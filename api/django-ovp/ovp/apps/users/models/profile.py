from django.db import models
from django.utils.translation import ugettext_lazy as _

from ovp.apps.channels.models import ChannelRelationship
from ovp.apps.users.helpers import get_settings, import_from_string

gender_choices = (
    ("male", "Male"),
    ("female", "Female"),
    ("unspecified", "Unspecified"),
)


class UserProfile(ChannelRelationship, models.Model):
    user = models.OneToOneField(
        "User",
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_profile",
        on_delete=models.DO_NOTHING
    )
    full_name = models.CharField(
        _("Full name"),
        max_length=300,
        null=True,
        blank=True)
    skills = models.ManyToManyField("core.Skill")
    causes = models.ManyToManyField("core.Cause")
    about = models.TextField(_("About me"), null=True, blank=True)
    department = models.CharField(
        _("Department"),
        max_length=300,
        null=True,
        blank=True)
    gender = models.CharField(
        _("Gender"),
        max_length=20,
        choices=gender_choices,
        default='unspecified')
    address = models.OneToOneField(
        'core.GoogleAddress',
        blank=True,
        null=True,
        verbose_name=_('address'),
        db_constraint=False,
        on_delete=models.DO_NOTHING
        )
    hidden_address = models.BooleanField(_('Hidden address'), default=False)
    birthday_date = models.DateField(blank=True, null=True)
    has_done_volunteer_work_before = models.NullBooleanField(
        _('Has done volunteer work before'), default=None)


def get_profile_model():
    s = get_settings()
    class_path = s.get("PROFILE_MODEL", None)
    if class_path:
        return import_from_string(class_path)
    return UserProfile
