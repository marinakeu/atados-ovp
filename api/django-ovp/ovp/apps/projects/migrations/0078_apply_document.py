# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-02-28 18:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0077_auto_20190204_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='apply',
            name='document',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name='Documento'),
        ),
    ]