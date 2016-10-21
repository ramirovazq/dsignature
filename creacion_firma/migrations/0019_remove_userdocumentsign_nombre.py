# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0018_auto_20150504_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdocumentsign',
            name='nombre',
        ),
    ]
