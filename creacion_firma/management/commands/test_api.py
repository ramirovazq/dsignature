# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import requests
import base64

class Command(BaseCommand):
    def handle(self, *args, **options):
        cer = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/aaa010101aaa_FIEL.cer"
        key = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/AAA010101AAA_FIEL.key"
        with open(cer, "rb") as cer_f:
            cer_encoded = base64.b64encode(cer_f.read())

        with open(key, "rb") as key_f:
            key_encoded = base64.b64encode(key_f.read())
        
        r = requests.post("http://127.0.0.1:8000/api_sign/", 
            json={'passwd': '12345678a', 'cer': cer_encoded, 'key': key_encoded})
