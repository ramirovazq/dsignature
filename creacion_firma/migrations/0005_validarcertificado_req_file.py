# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0004_validarcertificado'),
    ]

    operations = [
        migrations.AddField(
            model_name='validarcertificado',
            name='req_file',
            field=models.FileField(default='', upload_to=b''),
            preserve_default=False,
        ),
    ]
