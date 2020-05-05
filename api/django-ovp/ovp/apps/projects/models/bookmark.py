from django.db import models
from ovp.apps.core.models import AbstractBookmark


class ProjectBookmark(AbstractBookmark):

    project = models.ForeignKey('projects.Project', related_name='bookmarks', on_delete=models.DO_NOTHING)
