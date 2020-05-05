# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-09 18:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0004_auto_20170728_1903'),
        ('users', '0036_remove_user_channels'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='channel',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='user_channel',
                to='channels.Channel'),
            preserve_default=False,
        ),
    ]
