# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from creacion_firma.classes import DigitalSign


class Command(BaseCommand):
    good_text = """Response verify OK
/home/agmartinez/ocsp_3_uat/1024-v2/aimr770903ri4.pem: good
	This Update: Mar  7 17:21:28 2016 GMT
        """
    revoked_text = """Response verify OK
/home/agmartinez/ocsp_3_uat/1024-v2/aacf670505np1.pem: revoked
	This Update: Mar  7 17:06:54 2016 GMT
	Next Update: Mar  7 17:11:54 2016 GMT
	Reason: unspecified
	Revocation Time: Jun 12 21:53:29 2014 GMT"""
    def add_arguments(self, parser):
        parser.add_argument('--type',
                default=None,
                help='production, test')

    def handle(self, *args, **options):
        type_ocsp = options.get('type', "release")
        if type_ocsp == "test":
            self.check_certs_test()
        else:
            self.check_certs()
        #self.parse_ocsp_test_response()
        
    def check_certs(self):
        for user_pem_cer in settings.USER_CERTS_TEST:
            digital_sign = DigitalSign(cer_pem=user_pem_cer, test=False)
            print(user_pem_cer)
            print(digital_sign.get_info_cer(file_type="pem")["o"])
            print(digital_sign.get_info_cer(file_type="pem")["serial"])
            number = digital_sign.get_ocsp_origin(file_type="pem")
            OCSP_NUMBER = "C"+number
            print(OCSP_NUMBER)
            print(digital_sign.is_valid_ca_cer(settings.CERTS[OCSP_NUMBER]["chain"]))
            cer_is_valid = digital_sign.cert_is_valid(
                settings.CERTS[OCSP_NUMBER]["issuer"], 
                settings.CERTS[OCSP_NUMBER]["ocsp"])
            if cer_is_valid:
                print("valid")
            elif cer_is_valid is None:
                print("Error desconocido")
            else:
                print("not valid")

    def check_certs_test(self):
        user_pem_cers = ["/home/agmartinez/ocsp_3_uat/1024-v2/aacf670505np1.pem",
        "/home/agmartinez/ocsp_3_uat/1024-v2/aimr770903ri4.pem",
        "/home/agmartinez/ocsp_3_uat/1024-v2/cesj550110p99.pem"]
        for user_pem_cer in user_pem_cers:
            digital_sign = DigitalSign(cer_pem=user_pem_cer, test=True)
            print(user_pem_cer)
            print("CERT: ", digital_sign.get_ocsp_origin(file_type="pem"))
            print(digital_sign.get_info_cer(file_type="pem")["o"])
            if digital_sign.cert_is_valid(settings.CERTS["C0"]["issuer"], settings.CERTS["C0"]["ocsp"]):
                print("valid")
            else:
                print("not valid")

    def parse_ocsp_test_response(self):
        import re

        digital_sign = DigitalSign()
        for text in [self.good_text, self.revoked_text]:
            if digital_sign.ocsp_response(text):
                print("valid")
