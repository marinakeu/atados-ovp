# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-04 02:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0047_userprofile_birthday_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_login',
            field=models.BooleanField(default=False, verbose_name='Public'),
        ),
    ]
