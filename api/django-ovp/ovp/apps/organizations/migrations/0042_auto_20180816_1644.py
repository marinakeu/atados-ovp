# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-16 19:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0041_merge_20180814_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='is_inactive',
            field=models.BooleanField(default=False, verbose_name='Inactive'),
        ),
        migrations.AddField(
            model_name='organization',
            name='reminder_sent',
            field=models.BooleanField(default=False, verbose_name='Reminder'),
        ),
        migrations.AddField(
            model_name='organization',
            name='reminder_sent_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Reminder sent date'),
        ),
    ]
