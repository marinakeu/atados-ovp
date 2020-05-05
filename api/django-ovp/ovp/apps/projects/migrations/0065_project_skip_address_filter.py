# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-14 21:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0064_merge_20180822_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='skip_address_filter',
            field=models.BooleanField(
                default=False,
                verbose_name='Skip address filter'),
        ),
    ]