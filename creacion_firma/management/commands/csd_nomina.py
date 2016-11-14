# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from creacion_firma.utils import convert_nomina2xml

import os
import codecs
import datetime

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--password',
                default=None,
                help='password')
        parser.add_argument('--type',
                default="macro",
                help='construye el archivo para la macro o xml')
        parser.add_argument('--file',
                help='path donde se encuentra el archivo de excel con la nomina')
        parser.add_argument('--name',
                help='nombre de la quincena')
        parser.add_argument('--fecha-pago',
                help='la fecha de pago en formato YYYY-MM-DD')
        parser.add_argument('--periodicidad',
                default="QUINCENAL",
                help='la periodicidad del pago')

    def handle(self, *args, **options):
        password = options.get('password', "")
        path = options.get('file', "")
        f_type = options.get('type', "")
        name = options.get('name', "") #"QNA 14 ORD 2016"
        types = {"macro": "iim", "xml": "xml"}

        if f_type == "macro":
            cer = ""
            key = ""
            name_r = name.replace(" ", "<SP>")
        else:            
            #cer = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/aaa010101aaa_FIEL.cer"
            #key = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/AAA010101AAA_FIEL.key"
            cer = "/home/agmartinez/Descargas/Cert_Sellos/CSD01_AAA010101AAA.cer"
            key = "/home/agmartinez/Descargas/Cert_Sellos/CSD01_AAA010101AAA.key"
            name_r = name

        xmls = convert_nomina2xml(path, name_r, cer, key, password, options.get('fecha_pago', ""), f_type=f_type, periodicidad=options.get('periodicidad', "QUINCENAL"))
        url = "/tmp/{}/".format(name)
        if not os.path.exists(url):
            os.makedirs(url)

        #counter = 1
        for rfc, xml in xmls:
            with codecs.open(os.path.join(url, "{}.{}".format(rfc, types[f_type])), "wb", "utf-8") as f:
                f.write(xml)
        #    if counter == 2:
        #        break
        #    counter += 1

