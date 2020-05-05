# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-12-31 13:16
from __future__ import unicode_literals

from django.db import migrations
import django_resized.forms
import ovp.apps.uploads.models


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0015_auto_20181204_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedimage',
            name='image_large',
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=None,
                default=None,
                force_format=None,
                keep_meta=True,
                max_length=300,
                null=True,
                quality=0,
                size=[
                    1260,
                    936],
                upload_to=ovp.apps.uploads.models.ImageName('-large')),
        ),
        migrations.AlterField(
            model_name='uploadedimage',
            name='image_medium',
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=None,
                default=None,
                force_format=None,
                keep_meta=True,
                max_length=300,
                null=True,
                quality=0,
                size=[
                    420,
                    312],
                upload_to=ovp.apps.uploads.models.ImageName('-medium')),
        ),
        migrations.AlterField(
            model_name='uploadedimage',
            name='image_small',
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=None,
                default=None,
                force_format=None,
                keep_meta=True,
                max_length=300,
                null=True,
                quality=0,
                size=[
                    350,
                    260],
                upload_to=ovp.apps.uploads.models.ImageName('-small')),
        ),
    ]
