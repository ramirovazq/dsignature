# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from creacion_firma.models import User
from creacion_firma.utils import split_nomina, get_files_dir, link_pdf2curp, search_xml_files

#path_pdfs = "/home/agmartinez/Timbrado INMEGEN/TIMBRADO 2016/QNA 05 2016/pdfs/"
#path_timbrados = "/home/agmartinez/Timbrado INMEGEN/TIMBRADO 2016/QNA 05 2016/timbrados/"

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--curp',
                default=None,
                help='curp')
        parser.add_argument('--path-pdfs',
                default=None,
                help='path to pdfs')
        parser.add_argument('--path-timbrados',
                default=None,
                help='path to timbrado')

    def handle(self, *args, **options):
        curp = options.get('curp', "")
        path_pdfs = options.get('path_pdfs', "")
        path_timbrados = options.get('path_timbrados', "")
        triplet = self.find_xmls_pdfs_curp(path_pdfs, path_timbrados)
        data = self.triple_to_dict(triplet)
        print(data[curp])

    def find_xmls_pdfs_curp(self, path_pdfs, path_timbrados):
        path_tmp = "/tmp/pdfs/"
        pdf_files = get_files_dir(path_pdfs)
        num_files = 0
        for pdf_file in pdf_files:
            num_files += split_nomina(
                path_tmp, 
                path_pdfs+pdf_file,
                init=num_files)
        files = link_pdf2curp(num_files, path_tmp)
        curp_pdf_xml, pdf_no_xml, xml_no_pdf = search_xml_files(
            files, 
            path_timbrados)
        return curp_pdf_xml 

    def triple_to_dict(self, triplet):
        return dict((k, (x, p)) for k, x, p in triplet)
