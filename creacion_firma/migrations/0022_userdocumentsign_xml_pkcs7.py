# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0021_auto_20150618_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocumentsign',
            name='xml_pkcs7',
            field=models.FileField(null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
