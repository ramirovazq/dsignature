# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creacion_firma', '0007_auto_20150320_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=30)),
                ('curp', models.CharField(unique=True, max_length=40)),
                ('number_user', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='userdocumentsign',
            name='number_user',
        ),
        migrations.RemoveField(
            model_name='userdocumentsign',
            name='username',
        ),
        migrations.AddField(
            model_name='userdocumentsign',
            name='user',
            field=models.ForeignKey(default=None, to='creacion_firma.User'),
            preserve_default=False,
        ),
    ]
