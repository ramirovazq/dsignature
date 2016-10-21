# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0005_validarcertificado_req_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='validarcertificado',
            name='username',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
