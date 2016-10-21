# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0012_userdocumentsign_digital_sign_xml'),
    ]

    operations = [
        migrations.RenameField(
            model_name='certificado',
            old_name='der',
            new_name='pem',
        ),
    ]
