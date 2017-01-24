# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings

from creacion_firma.classes import CSD

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
        password = options.get('password', "12345678a")
        self.csd(password, type_ocsp)
        
    def csd(self, password, type_ocsp):
        cer = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/CSD01_AAA010101AAA.cer"
        key = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/CSD01_AAA010101AAA.key"
        cer_f = open(cer, "rb")
        key_f = open(key, "rb")
        digital_sign = CSD(cer=cer_f, key=key_f, test=type_ocsp == "test")
        cer_f.close()
        key_f.close()
        print(digital_sign.get_info_cer()["o"])
        number = digital_sign.get_ocsp_origin()
        OCSP_NUMBER = "C"+number
        print("ORIGINAL", OCSP_NUMBER)
        if type_ocsp == "test":
            OCSP_NUMBER = "C0"
        print(OCSP_NUMBER)
        print(digital_sign.sign(
            #"/home/agmartinez/csd_test/test_sello.xml",
            "/home/agmartinez/csd_test/QNA.xml", 
            #"/home/agmartinez/csd_test/SF.CadenaOriginal/ejemplo1cfdv3.xml",
            password,
            settings.CERTS[OCSP_NUMBER]["issuer"],
            settings.CERTS[OCSP_NUMBER]["ocsp"],
            settings.CERTS[OCSP_NUMBER]["chain"]))
        print("SIGN: ", digital_sign.verify_digest())
        print("NoCertificado: ", digital_sign.get_no_certificado())
        #print(digital_sign.cer2base64())
        print(digital_sign.digest_hex(digital_sign.files["sign"]["o_string"]))
        print("CLEAN")
        digital_sign.clean()
