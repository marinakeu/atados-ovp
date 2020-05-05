# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-11 16:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0022_auto_20161220_1914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='roles',
        ),
        migrations.AddField(
            model_name='volunteerrole',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='projects.Project', verbose_name='project'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='canceled',
            field=models.BooleanField(default=False, verbose_name='canceled'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='canceled_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='canceled date'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created date'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='email',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project', verbose_name='project'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='status',
            field=models.CharField(max_length=30, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='jobdate',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dates', to='projects.Job', verbose_name='job'),
        ),
        migrations.AlterField(
            model_name='project',
            name='address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.GoogleAddress', verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='project',
            name='applied_count',
            field=models.IntegerField(default=0, verbose_name='Applied count'),
        ),
        migrations.AlterField(
            model_name='project',
            name='causes',
            field=models.ManyToManyField(to='core.Cause', verbose_name='causes'),
        ),
        migrations.AlterField(
            model_name='project',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='uploads.UploadedImage', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='project',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Modified date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.Organization', verbose_name='organization'),
        ),
        migrations.AlterField(
            model_name='project',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='project',
            name='skills',
            field=models.ManyToManyField(to='core.Skill', verbose_name='skills'),
        ),
    ]