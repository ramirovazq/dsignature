# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0020_user_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='firmarcertificado',
            name='identificacion',
        ),
        migrations.RemoveField(
            model_name='firmarcertificado',
            name='username',
        ),
        migrations.AddField(
            model_name='firmarcertificado',
            name='user',
            field=models.ForeignKey(default=None, to='creacion_firma.User'),
            preserve_default=False,
        ),
    ]
