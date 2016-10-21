# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings

import datetime

#Pipeline: get_data_nomina->transfrom2xml->get_seal_and_nocert->transform2xml
percepciones = [{
"tipo": "001", "clave": "001a", "concepto": "SUELDO BASE", 
"importe_gravado": 9578.69, "importe_exento": 0.000000
}]

deducciones = [{
"tipo": "002", "clave": "001a", "concepto": "IMPUESTO SOBRE LA RENTA (ISR)", 
"importe_gravado": 4247.04, "importe_exento": 0.000000
}]

data_example = {
"total_neto": 14932.41,
"fecha_sello": "",
"sello": "",
"no_certificado": "",
"total_bruto": 20207.85,
"folio": "7075",
"nombre_usuario": "MARTINEZ ROMERO ALEJANDRO GILBERTO",
"rfc_usuario": "MARA800822JQ4",
"num_empleado": 155,
"nombre_nomina": "QNA 10 ORD 2016",
"total_impuestos_retenidos": 4247.04,
"curp": "MARA800822HDFRML00",
"tipo_regimen": "2",
"fecha_pago": "2016-05-25",
"fecha_inicial_pago": "2016-05-16",
"fecha_final_pago": "2016-05-31",
"num_dias_pagados": 15,
"departamento": "SUBDIRECCION DE SECUENCIACION Y GENOTIPIFICACION",
"clabe": "021180062725758480",
"puesto": "JEFE DE DEPARTAMENTO EN AREA MEDICA B",
"tipo_contrato": "CONFIANZA",
"periodicidad_pago": "QUINCENAL",
"percepcion_total_gravado": 20207.85,
"percepcion_total_exento": 0.000000,
"deduccion_total_gravado": 5275.44,
"deduccion_total_exento": 0.000000,
"percepciones": percepciones,
"deducciones": deducciones
}

from creacion_firma.utils import sign_xml
import codecs

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--password',
                default=None,
                help='password')

    def handle(self, *args, **options):
        cer = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/aaa010101aaa_FIEL.cer"
        key = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/AAA010101AAA_FIEL.key"
        xml_url = "/tmp/xml_sign.xml"
        password = options.get('password', "")
        data_example["fecha_sello"] = datetime.datetime.today().isoformat()
        xml = self.transform(data_example, "plantilla_nomina.xml")
        with codecs.open(xml_url, "wb", "utf-8") as f:
            f.write(xml)
        sign_verify, sign_base64, no_certificado = sign_xml(xml_url, cer, key, password, type_ocsp="test")
        if sign_verify is True:
            print("OK")
            data_example["sello"] = sign_base64
            data_example["no_certificado"] = no_certificado
            xml = self.transform(data_example, "plantilla_nomina.xml")
            print(xml)
        else:
            print("Error de verificacion de sello")

    def transform(self, data, plantilla_url):
        from django.template.loader import render_to_string
        xml = render_to_string(plantilla_url, data)
        xml = xml.replace("\n", "")
        return xml



