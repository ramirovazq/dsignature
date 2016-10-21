# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0014_auto_20150421_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocumentsign',
            name='nombre',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
