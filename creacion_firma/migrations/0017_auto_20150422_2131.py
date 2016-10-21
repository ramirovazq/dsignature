# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0016_transactionstatus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdocumentsign',
            name='fecha',
        ),
        migrations.AddField(
            model_name='userdocumentsign',
            name='transaction',
            field=models.ForeignKey(default=0, to='creacion_firma.TransactionStatus'),
            preserve_default=False,
        ),
    ]
