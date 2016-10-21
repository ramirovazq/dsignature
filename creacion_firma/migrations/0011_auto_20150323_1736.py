# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0010_userdocumentsign_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdocumentsign',
            name='fecha',
            field=models.DateField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
