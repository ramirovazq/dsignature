# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings

from creacion_firma.views import id_generator, SIZE_NAME
from creacion_firma.classes import DigitalSign, tmp_dir_o_file, tmp_prefix
from creacion_firma.models import UserDocumentSign
from creacion_firma.utils import create_docs_test
from subprocess import call

import datetime

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--type',
                default=None,
                help='production, test')
        parser.add_argument('--password',
                default=None,
                help='escribe la contraseña')

    def handle(self, *args, **options):
        type_ocsp = options.get('type', "production")
        password = options.get('password', "")
        self.sign(password, type_ocsp)
        
    def sign(self, password, type_ocsp):
        tmp_dir_pkcs7_file = tmp_prefix + "pkcs7_files_test/"
        tmp_dir_pkcs7_file_date = tmp_dir_pkcs7_file+datetime.date.today().strftime("%Y%m")
        call(["mkdir", tmp_prefix])
        call(["mkdir", tmp_dir_o_file])
        call(["mkdir", tmp_dir_pkcs7_file])
        call(["mkdir", tmp_dir_pkcs7_file_date])
        if type_ocsp == "test":
            user_document_sign = create_docs_test("PXXD941105MDFCZL09", tmp_dir_o_file, 1000, "test")
            cer = "/home/agmartinez/ocsp_3_uat/1024-v2/aimr770903ri4.cer"
            key = "/home/agmartinez/ocsp_3_uat/1024-v2/AIMR770903RI4.key"
        else:
            user_document_sign = create_docs_test("MARA800822HDFRML00", tmp_dir_o_file, 155, "agmartinez")
            cer = "/home/agmartinez/Documentos/FIEL 2013/FIEL_MARA800822JQ4_20130523120921/mara800822jq4.cer"
            key = "/home/agmartinez/Documentos/FIEL 2013/FIEL_MARA800822JQ4_20130523120921/Claveprivada_FIEL_MARA800822JQ4_20130523_120921.key"
        cer_f = open(cer, "rb")
        key_f = open(key, "rb")
        digital_sign = DigitalSign(cer=cer_f, key=key_f, test=type_ocsp == "test")
        cer_f.close()
        key_f.close()
        print(digital_sign.get_info_cer()["o"])
        number = digital_sign.get_ocsp_origin()
        OCSP_NUMBER = "C"+number
        if type_ocsp == "test":
            OCSP_NUMBER = "C0"
        print(digital_sign.sign(
            tmp_dir_pkcs7_file_date, 
            user_document_sign, 
            password,
            settings.CERTS[OCSP_NUMBER]["issuer"],
            settings.CERTS[OCSP_NUMBER]["ocsp"],
            settings.CERTS[OCSP_NUMBER]["chain"]))
        print("SIGN: ", digital_sign.verify(user_document_sign.xml.url))
        print(user_document_sign.xml_pkcs7.url)        
        print("CLEAN")
        digital_sign.clean()
        call(["rm", user_document_sign.xml_pkcs7.url])
        call(["rm", user_document_sign.xml.url])
        user_document_sign.delete()
