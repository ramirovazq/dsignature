# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0009_auto_20150320_2023'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocumentsign',
            name='fecha',
            field=models.DateField(default=datetime.date(2015, 3, 23), auto_now=True),
            preserve_default=False,
        ),
    ]
