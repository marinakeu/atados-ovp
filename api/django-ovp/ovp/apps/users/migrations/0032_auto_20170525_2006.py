# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-25 20:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_auto_20170525_1701'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passwordhistory',
            old_name='set_date',
            new_name='created_date',
        ),
    ]
