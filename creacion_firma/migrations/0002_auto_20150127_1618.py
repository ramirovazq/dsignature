# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserDocumentFirm',
            new_name='UserDocumentSign',
        ),
        migrations.RenameField(
            model_name='userdocumentsign',
            old_name='digital_firm',
            new_name='digital_sign',
        ),
    ]
