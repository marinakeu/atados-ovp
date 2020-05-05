from django.db import models
from ovp.apps.core.models import AbstractBookmark


class OrganizationBookmark(AbstractBookmark):
    organization = models.ForeignKey(
        'organizations.Organization',
        related_name='bookmarks',
        on_delete=models.DO_NOTHING
    )
