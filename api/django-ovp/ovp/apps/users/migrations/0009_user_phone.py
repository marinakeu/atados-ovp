# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-27 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20161007_2052'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(
                blank=True,
                max_length=30,
                null=True,
                verbose_name='Phone'),
        ),
    ]
