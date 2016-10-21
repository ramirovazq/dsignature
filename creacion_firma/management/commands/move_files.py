# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.exceptions import SuspiciousFileOperation
from django.conf import settings
from subprocess import call
from creacion_firma.models import UserDocumentSign
from creacion_firma.utils import id_generator

import os

SIZE_NAME = 30
tmp_prefix = settings.TMP_DIR
tmp_dir_pdf_file = tmp_prefix + "pdf_files/"
tmp_dir_xml_file = tmp_prefix + "xml_files/"

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--user-document-sign-id',
                default=None,
                help='curp')

    def handle(self, *args, **options):
        user_document_sign_id = options.get('user_document_sign_id', "")
        user_document_sign = UserDocumentSign.objects.get(id = user_document_sign_id)
        transaction_number = user_document_sign.transaction.number
        new_base_path_dir_pdf = "%sT%s" % (tmp_dir_pdf_file, transaction_number)
        new_base_path_dir_xml = "%sT%s" % (tmp_dir_xml_file, transaction_number)
        try:
            pdf_file = user_document_sign.document.path
        except SuspiciousFileOperation:
            pdf_file = user_document_sign.document.url

        try:
            xml_file = user_document_sign.xml.path
        except SuspiciousFileOperation:
            xml_file = user_document_sign.xml.url

        n_pdf_file = new_base_path_dir_pdf+"/"+id_generator(size=SIZE_NAME)
        n_xml_file = new_base_path_dir_xml+"/"+id_generator(size=SIZE_NAME)
        call(["cp", pdf_file, n_pdf_file])
        call(["cp", xml_file, n_xml_file])
        user_document_sign.document = n_pdf_file
        user_document_sign.xml = n_xml_file
        user_document_sign.save()
        print("moved PDF from {}".format(pdf_file))
        print("to {}".format(n_pdf_file))
        print("moved XML from {}".format(xml_file))
        print("to {}".format(n_xml_file))
        os.remove(pdf_file)
        os.remove(xml_file)
