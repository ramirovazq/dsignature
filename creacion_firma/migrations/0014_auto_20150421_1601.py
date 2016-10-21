# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0013_auto_20150323_1809'),
    ]

    operations = [
        migrations.CreateModel(
            name='FirmarCertificado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('req_file', models.FileField(upload_to=b'')),
                ('certificado', models.FileField(upload_to=b'')),
                ('identificacion', models.FileField(upload_to=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='ValidarCertificado',
        ),
    ]
