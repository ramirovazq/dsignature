from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from subprocess import call
from django.db import IntegrityError

import requests
import string
import random
import datetime

def split_nomina(path_tmp, path_filename, init=0):
    from PyPDF2 import PdfFileWriter, PdfFileReader
    inputpdf = PdfFileReader(open(path_filename, "rb"))

    for i in xrange(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open("%sdocument-page%s.pdf" % (path_tmp, i+init), "wb") as outputStream:
            output.write(outputStream)

    return inputpdf.numPages


def pdfparser(path_filenames):
    for path_filename in path_filenames:
        fp = file(path_filename, 'rb')
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
            yield (retstr.getvalue(), path_filename)


def locate_curp_text(data_text):
    import re
    pattern = ur"(?P<curp>\w{4}[0-9]{6}[A-Z]{6}[0-9]{2})"
    re_c = re.compile(pattern, re.UNICODE)
    matchs = {}
    for text, path_filename in data_text:
        match = re_c.search(text)
        if match:
            matchs[match.groupdict()["curp"]] = path_filename
    return matchs

def link_pdf2curp(num_files, path):
    filenames = ("%sdocument-page%s.pdf" % (path, i) for i in xrange(0, num_files))
    return locate_curp_text(pdfparser(filenames)).items()

def get_files_dir(directory):
    import os
    try:
        files = os.listdir(directory)
    except OSError:
        files = []

    for file_ in os.listdir(directory):
        yield file_

def sync_user(curp):
    from creacion_firma.models import User
    try:
        response = requests.get(
            "http://api.intranet.inmegen.gob.mx/api/protocolos/v1/usercurp/?format=json&curp=%s" % (curp,))
    except requests.exceptions.ConnectionError:
        return 0

    if response.status_code == 200:
        result = response.json()
        if result["meta"]["total_count"] > 0:
            user = result["objects"][0]
            try:
                return User.objects.create(
                    username=user["username"],
                    curp=user["curp"],
                    number_user=user["numero_de_empleado"],
                    token=build_token(user["curp"], user["numero_de_empleado"])
                )
            except IntegrityError:
                return -1
        else:
            return 0
    return response.status_code

def unzip(tmp_dir, file_):
    import zipfile
    with open(tmp_dir+"zip.zip", "wb") as f:
        f.write(file_.read())

    with zipfile.ZipFile(tmp_dir+"zip.zip", "r") as z:
        z.extractall(tmp_dir)

def clean_dir(directory):
    for f in get_files_dir(directory):
        call(["rm", directory+f])

def xml_reader(xml_directory, xml_files):
    curps = {}
    for xml_file in xml_files:
        with open(xml_directory+xml_file) as f:
            yield (f.read(), xml_directory+xml_file)

def search_xml_files(files, xml_directory):
    xml_files = get_files_dir(xml_directory)
    curps_xml = locate_curp_text(xml_reader(xml_directory, xml_files))
    data = []
    pdf_no_xml = set([])
    matched = set([])
    for curp, pdf in files:
        try:
            data.append((curp, pdf, curps_xml[curp]))
            matched.add(curp)
        except KeyError:
            pdf_no_xml.add(curp)

    all_curp_xml = set(curps_xml.keys())
    xml_no_pdf = all_curp_xml.difference(matched)
    return data, pdf_no_xml, xml_no_pdf

def get_curp_xml_files(xml_directory):
    xml_files = get_files_dir(xml_directory)
    curps_xml = locate_curp_text(xml_reader(xml_directory, xml_files))
    return curps_xml.items()

def get_curp2username(curps, sin_curp_intranet):
    from creacion_firma.models import User
    users = []
    for curp in curps:
        try:
            user = User.objects.get(curp=curp)
        except User.DoesNotExist:
            user = sync_user(curp)
        if user == 0:
            sin_curp_intranet.append(curp)
        elif user == -1:
            print "Curp diferente en la intranet y el local"
        else:
            users.append(user.username)
    return users

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def save_file(filename, data):
    with open(filename, "wb") as f:
        for line in data.readlines():
            f.write(line)

def convert_str2date(date_text):
    dict_ = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", 
    "jun": "06", "jul": "07", "aug": "08", "sep": "09", "oct": "10",
    "nov": "11", "dic": "12"}
    date_list = date_text.split(" ")
    month_key = date_list[0].replace("notAfter=", "").lower()
    try:
        month = dict_[month_key.strip()]
        date_text = month + " " + " ".join(date_list[1:])
        return datetime.datetime.strptime(date_text, "%m %d %H:%M:%S %Y GMT")
    except ValueError:
        return datetime.datetime.strptime(date_text, "%m %d %H:%M:%S %Y")
    except KeyError:
        return None

def parse_info_cer(info):
    indexs = [(info.find("subject="), "subject"), 
        (info.find("issuer="), "issuer"), 
        (info.find("serial="), "serial"),
        (info.find("Modulus="), "modulus"), 
        (info.find("SHA1 Fingerprint="), "fingerprint")] 
    indexs.sort()
    values = {}
    for index_key in zip(indexs[:], indexs[1:]) + [(indexs[-1], (-1, ""))]:
        from_index, key = index_key[0]
        to_index, _ = index_key[1]
        values[key] = info[from_index:to_index].replace("\n", "").strip()
    
    index = values["subject"].find("notAfter")
    subject = values["subject"][:index].strip()
    date_txt = values["subject"][index:].strip()
    index_serial_number = subject.find("serialNumber=")
    serial_number = subject[index_serial_number+len("serialNumber="):index_serial_number+len("serialNumber=")+18]
    data_subject_issuer = sorted(values["issuer"].split("/")[1:])

    subject_values = {}
    for data in sorted(subject.split("/")):
        if "=" in data:
            v, k = data.split("=")
            subject_values[v] = k

    try:        
        IC, ICN, _, IO = data_subject_issuer[:4]
    except ValueError:
        IC, ICN, IO = "", "", "" 

    return {"c": subject_values.get("C", ""), 
            "o": subject_values["O"], 
            "cn": subject_values["CN"], 
            "dateend": convert_str2date(date_txt),
            "ic": IC, 
            "io": IO, 
            "icn": ICN, 
            "fingerprint": values["fingerprint"], 
            "modulus": values["modulus"], 
            "curp": serial_number, 
            "serial": values["serial"]}

def clean(files):
    for filename in files:
        call(["rm", filename])

def create_docs_test(curp, path):
    from creacion_firma.models import User, UserDocumentSign, TransactionStatus
    call(["mkdir", path])
    SIZE_NAME = 30
    n_xml_file = path+"/"+id_generator(size=SIZE_NAME)
    with open(n_xml_file, 'wb') as f:
        f.write("TEST")

    user, _ = User.objects.get_or_create(curp=curp, number_user=155)
    transaction = TransactionStatus.objects.create(status="created")
    transaction_number = transaction.fecha.strftime("%Y%m%d") + "_" + str(transaction.id)

    return UserDocumentSign.objects.create(
        nomina=None,
        user=user,
        document=None,
        transaction=transaction,
        xml=n_xml_file)

def build_token(curp, numero_de_empleado):
    from django.conf import settings
    import hashlib
    import datetime
    time_key = datetime.datetime.utcnow().strftime("%Y%m%d%H")
    data = curp + str(numero_de_empleado) + time_key
    return hashlib.sha256(data+settings.MAGIC_NUMBER).hexdigest()

def sign_xml(xml_url, cer, key, password, type_ocsp="production"):
    from django.conf import settings
    from creacion_firma.classes import CSD
    cer_f = open(cer, "rb")
    key_f = open(key, "rb")
    digital_sign = CSD(cer=cer_f, key=key_f, test=type_ocsp == "test")
    cer_f.close()
    key_f.close()
    number = digital_sign.get_ocsp_origin()
    OCSP_NUMBER = "C"+number
    digital_sign.sign(
        xml_url, 
        password,
        settings.CERTS[OCSP_NUMBER]["issuer"],
        settings.CERTS[OCSP_NUMBER]["ocsp"],
        settings.CERTS[OCSP_NUMBER]["chain"])
    sign_verify = digital_sign.verify_digest()
    no_certificado = digital_sign.get_no_certificado()
    sign_base64 = digital_sign.view_base64_sign()
    certificado = digital_sign.cert_base64()
    digital_sign.clean()
    return sign_verify, sign_base64, no_certificado, certificado


def read_catalog_percepciones_deducciones(tipo):
    import os
    if tipo == "percepciones":
        filename = "resultado_percepciones.csv"
    else:
        filename = "resultado_deducciones.csv"
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../' + filename))
    codes = {}
    with open(path) as f:
        line = f.readline()
        while line:
            tipo_text = line.split(";")[0]
            tipo_code = line.split(";")[1]
            codes[tipo_code] = tipo_text
            line = f.readline()
    return codes

def convert_nomina2xml(excel_path, name, cer, key, password, fecha_pago, periodicidad="QUINCENAL", f_type='macro'):
    import pandas as pd
    from creacion_firma.classes import UserXMLData

    data_transform = {
        "Nombre": "nombre_usuario",
        "RFC": "rfc_usuario",
        "CURP": "curp",
        u"DENOMINACI\xd3N DEL PUESTO": "puesto",
        "ADSCRIPCION": "departamento",
        "Empl": "num_empleado",
        #"Plaza": "",
        #"CLAVE PRESUPUESTAL": "",
        #"CODIGO DEL PUESTO": "",
        #"CENTRO DE RESPONSABILIDAD": "",
        "PERIODO DE PAGO": "fecha_pago",
        "TIPO DE NOMBRAMIENTO": "tipo_contrato",
        #"PRESTAMO A CORTO O MEDIANO PLAZO": "",
        u"N\xdaMERO DE D\xcdAS": "num_dias_pagados",
        "CUENTA CLABE": "clabe",
        #"Neto a Pagar": "percepcion_total_gravado"
    }

    df = pd.read_excel(excel_path, keep_default_na=False)
    columns = list(df.columns)
    catalogo_percepciones = read_catalog_percepciones_deducciones("percepciones")
    catalogo_deducciones = read_catalog_percepciones_deducciones("deducciones")
    if f_type == "macro":
        conceptos = {c: c.replace(" ", "<SP>") for c in columns}
        catalogo_percepciones = {k: v.replace(" ", "<SP>") for k, v in catalogo_percepciones.items()}
        catalogo_deducciones = {k: v.replace(" ", "<SP>") for k, v in catalogo_deducciones.items()}
    else:
        conceptos = {c: c for c in columns}

    claves = [row for index, row in df[1:2].iterrows()][0]
    tipo = [row for index, row in df[0:1].iterrows()][0]
    for index, row in df[2:].iterrows():
        folio = str(index) if f_type == "macro" else str(index).zfill(5)
        user_xml_data = UserXMLData(name, fecha_pago, folio)
        percepciones_column = True
        for column in columns:
            if percepciones_column is True and len(claves[column]) > 0 and claves[column] != "Total":
                if row[column] > 0:
                    user_xml_data.add_percepciones({"clave": claves[column], 
                        "concepto": conceptos[column], "importe_gravado": row[column], 
                        "importe_exento": 0.000000, "tipo": str(tipo[column]).zfill(3), 
                        "tipo_text": catalogo_percepciones[claves[column]]})
            elif claves[column] == "Total":
                percepciones_column = False
            elif len(claves[column]) > 0 and claves[column] != "Total":
                if row[column] > 0:
                    user_xml_data.add_deducciones({"clave": claves[column], 
                        "concepto": conceptos[column], "importe_gravado": row[column], 
                        "importe_exento": 0.000000, "tipo": str(tipo[column]).zfill(3),
                        "tipo_text": catalogo_deducciones[claves[column]]})
            else:
                try:
                    if "CUENTA CLABE" == column:
                        if row[column].startswith("0"):
                            row[column] = row[column][1:]
                    elif data_transform[column] == "puesto" and f_type == "macro":
                        row[column] = row[column].replace(" ", "<SP>")
                    elif data_transform[column] == "departamento" and f_type == "macro":
                        row[column] = row[column].replace(" ", "<SP>")
                    user_xml_data.add(data_transform[column], row[column])
                except KeyError:
                    pass
        total_percepciones = user_xml_data.total_percepciones()
        total_deducciones = user_xml_data.total_deducciones()
        total_neto = round(total_percepciones - total_deducciones, 2)
        user_xml_data.add("total_bruto", total_percepciones)
        user_xml_data.add("total_neto", total_neto)
        deducciones = user_xml_data.deducciones()
        user_xml_data.add("total_impuestos_retenidos", deducciones["001a"]["importe_gravado"]) #ISR
        user_xml_data.add("deduccion_total_exento", round(total_deducciones, 2))
        user_xml_data.add("periodicidad_pago", periodicidad)
        user_xml_data.add("percepcion_total_gravado", total_percepciones)
        user_xml_data.transform_date()
        print(user_xml_data.data_template["nombre_usuario"], folio)
        user_xml_data.data_template["nombre_usuario"] = user_xml_data.data_template["nombre_usuario"] .replace(" ", "<SP>")
        if total_neto != round(row["Neto a Pagar"], 2):
            print("PERCEPCIONES", total_percepciones, "DEDUCCIONES", total_deducciones)
            print("ERROR AL COMPARAR EL TOTAL CON EL NETO")
            print(total_neto, round(row["Neto a Pagar"], 2))
            break
        else:
            if f_type == 'xml':
                yield (user_xml_data.rfc, user_xml_data.transform2xml_signed(cer, key, password))
            else:
                yield (user_xml_data.rfc, 
                        user_xml_data.transform("plantilla_nomina_macro.txt", compress=False))

def transform_template2xml(plantilla_url, data_template, compress=True):
    from django.template.loader import render_to_string
    xml = render_to_string(plantilla_url, data_template)
    if compress:
        xml = xml.replace("\n", "")
        xml = " ".join(xml.split())
    return xml

def comprobantes2xml(comprobantes, limit=1):
    data_template = {"paquete_id": None, "total_regs": None, "comprobantes": None}
    comprobatntes_xml = []
    count = 0
    for curp, xml in comprobantes:
        comprobatntes_xml.append({"id": curp, "xml": xml})
        count += 1
        if limit == count:
            break
            
    data_template["paquete_id"] = "123456"
    data_template["total_regs"] = len(comprobatntes_xml)
    data_template["comprobantes"] = comprobatntes_xml
    return transform_template2xml("plantilla_nomina_blob.xml", data_template)
