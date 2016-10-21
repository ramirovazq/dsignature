# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

import zipfile
import io
import codecs
from azure.storage.blob import BlockBlobService, ContentSettings
from creacion_firma.utils import convert_nomina2xml, comprobantes2xml

ACCOUNT_NAME = "intgnomina"
SAS_TOKEN = "sr=c&si=ReadWrite&sig=Gb6%2Br6fa%2BOQtnvkMlaq0zUmasXNOD82qxVHpj083luA%3D"
CONTAINER_NAME = "contenedorarchivosais8012085l7"

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--password',
                default=None,
                help='password')

    def handle(self, *args, **options):
        password = options.get('password', "")
        buffer_bytes = self.create_zip(self.convert_nomina_to_xml(password))
        blob_uri = self.send_data_to_blob(buffer_bytes, "test123"))
        #print(self.send_data_to_blob("", "test123"))
        #self.get_data_from_blob("test123")

    def get_blob_meta(self, blob_name):
        blob_service = BlockBlobService(account_name=ACCOUNT_NAME, sas_token=SAS_TOKEN)
        return blob_service.get_blob_metadata(CONTAINER_NAME, blob_name)

    def convert_nomina_to_xml(self, password):
        path = "/home/agmartinez/Programas/firma_electronica/nomina10.xls"
        cer = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/aaa010101aaa_FIEL.cer"
        key = "/home/agmartinez/csd_test/Cert_Sellos/Cert_Sellos/AAA010101AAA_FIEL.key"
        comprobantes = convert_nomina2xml(path, "QNA 10 ORD 2016", cer, key, password, "2016-06-07")
        xml = comprobantes2xml(comprobantes, limit=2)
        #with codecs.open("/home/agmartinez/Escritorio/01.xml", "w", "utf8") as f:
        #    f.write(xml)
        return xml

    def create_zip(self, data):
        buffer_bytes = io.BytesIO()
        with zipfile.ZipFile(buffer_bytes, "a", zipfile.ZIP_DEFLATED, False) as myzip:
            myzip.writestr("01.xml", data.encode('utf-8'))
            # Mark the files as having been created on Windows so that
            # Unix permissions are not inferred as 0000
            for zfile in myzip.filelist:
                zfile.create_system = 0
        buffer_bytes.seek(0)
        return buffer_bytes

    def send_data_to_blob(self, data, blob_name):
        from azure.storage.blob.baseblobservice import _get_path
        blob_service = BlockBlobService(account_name=ACCOUNT_NAME, sas_token=SAS_TOKEN)
        blob_service.create_blob_from_stream(CONTAINER_NAME, blob_name, data, 
            content_settings=ContentSettings(
                content_type='application/zip', 
                content_disposition='attachment; filename="nch-outfile.zip"'))
        return '{}://{}{}'.format(
            blob_service.protocol,
            blob_service._get_host(),
            _get_path(CONTAINER_NAME, blob_name))

    def get_data_from_blob(self, blob_name):
        blob_service = BlockBlobService(account_name=ACCOUNT_NAME, sas_token=SAS_TOKEN)
        blob_service.get_blob_to_path(CONTAINER_NAME, blob_name, "/home/agmartinez/Escritorio/blob.zip")

    def write(self, zip_file):
        with open("/home/agmartinez/Escritorio/blob.zip", "w") as f:
            f.write(zip_file.read())

