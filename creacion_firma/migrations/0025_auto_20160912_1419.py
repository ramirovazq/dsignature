# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-12 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0024_auto_20160426_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdocumentsign',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to=b''),
        ),
    ]
