# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-04 19:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0060_auto_20171214_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='address',
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.GoogleAddress',
                verbose_name='address'),
        ),
    ]