# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-28 19:14
from __future__ import unicode_literals

from django.db import migrations

def forward_func(apps, schema_editor):
    Channel = apps.get_model('channels', 'Channel')
    Category = apps.get_model('projects', 'Category')
    channel = Channel.objects.get(slug='default')
    Category.objects.create(name="Export to shell", slug="atados-to-shell", channel=channel)
    return True

def rewind_func(apps, schema_editor):
    return True

class Migration(migrations.Migration):

    dependencies = [
        ('shell', '0002_disable_email_verification_email')
    ]

    operations = [
        migrations.RunPython(forward_func, rewind_func)
    ]