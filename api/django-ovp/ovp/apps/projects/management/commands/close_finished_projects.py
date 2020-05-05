# -*- coding: utf-8 -*-
import sys

from django.core.management.base import BaseCommand
from django.utils import timezone
from ovp.apps.projects.models import Project


class Command(BaseCommand):

    help = "Close projects which have a Job and end_date has already passed"

    def handle(self, *args, **options):
        projects = Project.objects.filter(
            closed=False,
            job__end_date__lt=timezone.now()
        )
        print("Closing {} finished projects".format(projects.count()))

        for project in projects:
            # Do not use update because of signals
            project.closed = True
            project.save()
