# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from creacion_firma.models import User
from creacion_firma.utils import get_files_dir, pdfparser

import os
#path_pdfs = "/home/agmartinez/Timbrado INMEGEN/TIMBRADO 2016/QNA 05 2016/pdfs/"

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--clave',
                default=None,
                help='clave presupuestal')
        parser.add_argument('--curp',
                default=None,
                help="")
        parser.add_argument('--path',
                default=None,
                help='path to files')

    def handle(self, *args, **options):
        clave = options.get('clave', "")
        path = options.get('path', "")
        if clave:
            self.find_clave(clave, path)
        else:
            curp = options.get('curp', "")
            self.find_curp(curp, path)

    
    def find_clave(self, clave, path):
        pdf_files = get_files_dir(path)
        data_path = pdfparser([os.path.join(path, f) for f in pdf_files])
        for data, path in data_path:
            if data.find(clave) != -1:
                print(clave, path)
                break

    def find_curp(self, curp, path):
        files = get_files_dir(path)
        for file_ in [os.path.join(path, f) for f in files]:
            with open(file_, 'r') as f:
                if f.read().find(curp) != -1:
                    print(curp, file_)
                    break
