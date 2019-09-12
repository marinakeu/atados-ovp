# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-03 08:41
from __future__ import unicode_literals

from django.db import migrations

from ovp.apps.core.helpers import generate_slug

COUNTRY_MANAGER_GROUP_LIST = [
  'mng-ar', 'mng-bo', 'mng-cl', 'mng-co', 'mng-ec', 'mng-gt', 'mng-hn', 'mng-cr', 'mng-mx', 'mng-ni', 'mng-pa', 'mng-py', 'mng-pe', 'mng-do', 'mng-uy', 'mng-ve'
]


COUNTRY_MANAGER_PERM_LIST = [
  'Can add address component', 'Can change address component', 'Can delete address component',
  'Can add address component type', 'Can change address component type', 'Can delete address component type',
  'Can add google address', 'Can change google address', 'Can delete google address', 'Can add google region',
  'Can change google region', 'Can delete google region', 'Can add Lead', 'Can change Lead', 'Can delete Lead',

  'Can change organization',

  'Can change apply', 'Can change Job', 'Can change job date', 'Can change project', 'Can add role',
  'Can add volunteer role', 'Can change role', 'Can change volunteer role', 'Can delete role',
  'Can delete volunteer role', 'Can change work',

  'Can add uploaded image', 'Can change uploaded image',
  'Can add uploaded file', 'Can change uploaded file', 'Can delete uploaded file',
]

def forwards_func(apps, schema_editor):
  Group = apps.get_model("auth", "Group")
  Permission = apps.get_model("auth", "Permission")
  permissions = Permission.objects.values_list('id', flat=True).filter(name__in=COUNTRY_MANAGER_PERM_LIST).all()

  for group_name in COUNTRY_MANAGER_GROUP_LIST:
    if Group.objects.filter(name=group_name).count() == 0:
      group = Group.objects.create(name=group_name)
      for perm_id in (permissions):
        group.permissions.add(perm_id)


def rewind_func(apps, schema_editor):
  Group = apps.get_model("auth", "Group")
  Group.objects.filter(name__in=COUNTRY_MANAGER_GROUP_LIST).delete()

class Migration(migrations.Migration):
  dependencies = [
    ('gdd', '0001_initial'),
  ]

  operations = [
    migrations.RunPython(forwards_func, rewind_func)
  ]
