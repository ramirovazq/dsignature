# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0006_validarcertificado_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('fingerprint', models.CharField(unique=True, max_length=255)),
                ('der', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='userdocumentsign',
            name='certificado',
            field=models.ForeignKey(blank=True, to='creacion_firma.Certificado', null=True),
            preserve_default=True,
        ),
    ]
