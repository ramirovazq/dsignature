# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0008_auto_20150320_2014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificado',
            name='username',
        ),
        migrations.AddField(
            model_name='certificado',
            name='user',
            field=models.ForeignKey(default=None, to='creacion_firma.User'),
            preserve_default=False,
        ),
    ]
