# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0002_auto_20150127_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocumentsign',
            name='xml',
            field=models.FileField(default='', upload_to=b''),
            preserve_default=False,
        ),
    ]
