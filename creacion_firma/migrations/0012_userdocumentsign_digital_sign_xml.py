# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0011_auto_20150323_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocumentsign',
            name='digital_sign_xml',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
