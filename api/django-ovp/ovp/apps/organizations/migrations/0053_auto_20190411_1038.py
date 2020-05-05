# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-11 13:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0052_merge_20190327_1644'),
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
                to='core.SimpleAddress',
                verbose_name='address'),
        ),
    ]