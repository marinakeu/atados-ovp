# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-11 10:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0018_section_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='type',
            field=models.CharField(
                choices=[
                    ('projects',
                     'Projects'),
                    ('organizations',
                     'Organizations')],
                default='',
                max_length=30,
                verbose_name='Section type'),
        ),
    ]
