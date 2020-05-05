# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-26 19:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ovp.apps.channels.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0007_channelsetting'),
        ('catalogue', '0005_auto_20170925_2203'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryFilter',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('channel',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='categoryfilter_channel',
                     to='channels.Channel')),
            ],
            options={
                'abstract': False,
            },
            bases=(
                ovp.apps.channels.models.mixins.ChannelCreatorMixin,
                models.Model),
        ),
    ]