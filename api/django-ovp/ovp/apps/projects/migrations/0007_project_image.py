# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-26 13:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0003_uploadedimage_uuid'),
        ('projects', '0006_auto_20161025_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='image',
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to='uploads.UploadedImage'),
            preserve_default=False,
        ),
    ]