# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0017_auto_20150422_2131'),
    ]

    operations = [
        migrations.CreateModel(
            name='NominaSubida',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
                ('visible', models.BooleanField(default=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='userdocumentsign',
            name='nomina',
            field=models.ForeignKey(blank=True, to='creacion_firma.NominaSubida', null=True),
            preserve_default=True,
        ),
    ]
