# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-18 11:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0045_user_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='details',
        ),
    ]