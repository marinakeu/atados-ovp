# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-03 08:41
from __future__ import unicode_literals

from django.db import migrations

from ovp.apps.core.helpers import generate_slug

def foward_func(apps, schema_editor):
    Channel = apps.get_model("channels", "Channel")
    channel = Channel.objects.create(name="Roche", slug="roche")
    Skill = apps.get_model("core", "Skill")
    Cause = apps.get_model("core", "Cause")


    Skill.objects.filter(channel=channel).delete()
    Cause.objects.filter(channel=channel).delete()

def rewind_func(apps, schema_editor):
    return True

class Migration(migrations.Migration):

    dependencies = [
        ('roche', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(foward_func, rewind_func)
    ]
