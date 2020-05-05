# -*- coding: utf-8 -*-
import sys

from django.core.management.base import BaseCommand
from django.utils import timezone
from ovp.apps.projects.models import Project


class Command(BaseCommand):

    help = "Close projects that have been filled"

    def handle(self, *args, **options):
        projects = Project.objects.filter(closed=False)

        for project in projects:
            role_count = project.roles.count()
            is_filled = True

        for role in project.roles.all():
            if role.vacancies > role.apply_set.count():
                is_filled = False
                break

        if is_filled:
            print("Closing filled project {}".format(project.slug))
            project.closed = True
            project.save()
