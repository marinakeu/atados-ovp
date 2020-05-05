# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-08-15 17:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import ovp.apps.channels.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0009_remove_channel_subchannels'),
        ('users', '0057_user_flairs'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('token',
                 models.CharField(
                     max_length=128,
                     verbose_name='Token')),
                ('created_date',
                 models.DateTimeField(
                     auto_now_add=True,
                     null=True,
                     verbose_name='Created date')),
                ('used_date',
                 models.DateTimeField(
                     blank=True,
                     default=None,
                     null=True,
                     verbose_name='Used date')),
                ('channel',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='emailverificationtoken_channel',
                     to='channels.Channel')),
                ('user',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.CASCADE,
                     to=settings.AUTH_USER_MODEL)),
            ],
            bases=(
                ovp.apps.channels.models.mixins.ChannelCreatorMixin,
                models.Model),
        ),
    ]