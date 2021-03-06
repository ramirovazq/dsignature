# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import requests
import base64

class Command(BaseCommand):
    def handle(self, *args, **options):
        #cer = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/aaa010101aaa_FIEL.cer"
        #key = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/AAA010101AAA_FIEL.key"
        #cer = "/home/agmartinez/ocsp_3_uat/1024-v2/aacf670505np1.cer" #REVOKED
        #key = "/home/agmartinez/ocsp_3_uat/1024-v2/AACF670505NP1.key"

        cer = "/home/agmartinez/ocsp_3_uat/1024-v2/aimr770903ri4.cer" #OK
        key = "/home/agmartinez/ocsp_3_uat/1024-v2/AIMR770903RI4.key"

        with open(cer, "rb") as cer_f:
            cer_encoded = base64.b64encode(cer_f.read())

        with open(key, "rb") as key_f:
            key_encoded = base64.b64encode(key_f.read())
        
        files_to_sign = [
            "/home/agmartinez/csd_test/QNA.xml",
            "/home/agmartinez/tmp/firma_electronica/files/image.jpeg",
            "/home/agmartinez/tmp/firma_electronica/files/guia_rapida_de_citas_apa.pdf"]

        for file_to_sign in files_to_sign:
            with open(file_to_sign, "rb") as f:
                file = base64.b64encode(f.read())
            r = requests.post("http://127.0.0.1:8000/api_sign/", 
                json={'passwd': '12345678a', 'cer': cer_encoded, 'key': key_encoded, "file": file})
            print(r.status_code)
            print(r.text)
