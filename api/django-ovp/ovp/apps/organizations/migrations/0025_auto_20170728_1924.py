# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-28 19:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0024_merge_20170712_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='address',
            field=models.OneToOneField(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.GoogleAddress',
                verbose_name='address'),
        ),
    ]