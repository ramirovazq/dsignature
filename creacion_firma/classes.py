# -*- coding: utf-8 -*-
from django.conf import settings
from creacion_firma.utils import id_generator, save_file, parse_info_cer, clean
from subprocess import STDOUT, PIPE, Popen
from creacion_firma.models import Certificado

import shlex
import datetime
import codecs
import pytz

SIZE_NAME = 30
tmp_prefix = settings.TMP_DIR
tmp_dir_o_file = tmp_prefix + "o_files/"

def run(function):
    def view(*args, **kwargs):
        command = function(*args, **kwargs)
        proc = Popen(shlex.split(command), stderr=STDOUT, stdout=PIPE)
        return proc.communicate()[0]
    return view

class DigitalSign(object):
    def __init__(self, cer=None, key=None, cer_pem=None, test=False):
        self.files = {}
        path_file_key = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        path_file_keypem = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        path_file_cer = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        if cer_pem is None:
            path_file_cerpem = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        else:
            path_file_cerpem = cer_pem

        self.files["key"] = {"der": path_file_key, "pem": path_file_keypem}
        self.files["cer"] = {"der": path_file_cer, "pem": path_file_cerpem, "pubkey": None}
        self.files["sign"] = {"digest": None, "base64": None, "o_string": None, 
            "sello": None, "pkcs7": None}
        self.files["transform"] = {}
        self.user_info_cer = None
        self.test = test
        if cer is not None:
            save_file(path_file_cer, cer)
            error = self.cer2pem()
            if error:
                self.clean()
                raise Exception, "PEM", "No se puede convertir a pem el certificado"
        if key is not None:
            save_file(path_file_key, key)

    @run
    def key2pem(self, password):
        command = "openssl pkcs8 -inform DER -in {filename} -passin pass:{password} -out {pem}".format(
            filename=self.files["key"]["der"],
            pem=self.files["key"]["pem"], 
            password=password)
        return command

    @run
    def cer2pem(self):
        command = "openssl x509 -in {cer} -inform DER -out {pem} -outform PEM".format(
                cer=self.files["cer"]["der"],
                pem=self.files["cer"]["pem"])
        return command

    @run
    def info_cer(self, file_type="der"):
        command = "openssl x509 -inform {file_type} -in {cer} -subject -noout -enddate -issuer -serial -modulus -fingerprint".format(
            file_type=file_type,
            cer=self.files["cer"][file_type])
        return command

    def cert_base64(self):
        pem = self.get_value_from_file("cer", "pem")
        pem = pem.replace(" ",'').split()
        return ''.join(pem[1:-1])

    def get_info_cer(self, file_type="der"):
        if self.user_info_cer is None:
            info = self.info_cer(file_type=file_type)
            self.user_info_cer = parse_info_cer(info)
        return self.user_info_cer
        
    @run
    def __key_modulus(self):
        command = "openssl rsa -noout -modulus -in {key_pem}".format(
            key_pem=self.files["key"]["pem"])
        return command

    def key_modulus(self):
        return self.__key_modulus().replace("\n", "").strip()

    @run
    def sign_pkcs7(self, pkcs7_dir, xml_url):
        new_base_path_dir_pkcs7 = "{name_dir}/{name_file}".format(
            name_dir=pkcs7_dir,
            name_file=id_generator(size=SIZE_NAME))
        command = "openssl cms -sign -binary -nodetach -noattr -md sha256 -in {xml_file} -outform DER -out {pkcs7_file} -signer {cer_pem} -inkey {key_pem}".format(
            xml_file=xml_url,
            pkcs7_file=new_base_path_dir_pkcs7,
            cer_pem=self.files["cer"]["pem"],
            key_pem=self.files["key"]["pem"]
        )
        self.set_pkcs7(new_base_path_dir_pkcs7)
        return command

    @run
    def __pkcs12(self, password):
        self.files["transform"]["pkcs12"] = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        command = "openssl pkcs12 -export -inkey {key_pem} -in {cer_pem} -out {pfx_file} -password pass:{password}".format(
            key_pem=self.files["key"]["pem"],
            cer_pem=self.files["cer"]["pem"],
            pfx_file=self.files["transform"]["pkcs12"],
            password=password
        )
        return command

    def to_pkcs12(self, password):
        self.key2pem(password)
        self.__pkcs12(password)
        tmp_file = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        self.base64(self.files["transform"]["pkcs12"], tmp_file)
        with open(tmp_file, 'rb') as f:
            base64 = f.read()
        clean([tmp_file])
        return base64

    def set_pkcs7(self, file_url):
        self.files["sign"]["pkcs7"] = file_url

    @run
    def ocsp(self, hacienda_cer_path, ocsp_cer):
        #### The ocsp's url can be find with the command 
        #### openssl x509 -noout -ocsp_uri -in OCSP_AC_4096_SHA256.pem
        #### Note: issuer is the certificate chain 
        if self.test:
            url = "https://cfdit.sat.gob.mx/edofiel"
            host = "cfdit.sat.gob.mx"
        else:
            url = "https://cfdi.sat.gob.mx/edofiel"
            host = "cfdi.sat.gob.mx"

        command = 'openssl ocsp -issuer {issuer} -cert {user_cer} -VAfile {ocsp_cer} -url {url} -header "HOST" "{host}"'.format(
                issuer=hacienda_cer_path,
                user_cer=self.files["cer"]["pem"],
                ocsp_cer=ocsp_cer,
                url=url,
                host=host)
        return command

    def ocsp_response(self, text):
        import re
        response_pattern = ur"(?P<verify>Response verify OK)"
        re_c = re.compile(response_pattern, re.UNICODE)
        match = re_c.search(text)
        if not match:
            return None
        #print(match.groupdict()["verify"])

        revoke_pattern = ur"(?P<revoked>revoked)"
        re_c = re.compile(revoke_pattern, re.UNICODE)
        match = re_c.search(text)
        if match:
            #print(match.groupdict()["revoked"])
            return False

        good_pattern = ur"(?P<good>good)"
        re_c = re.compile(good_pattern, re.UNICODE)
        match = re_c.search(text)
        if match:
            #print(match.groupdict()["good"])
            return True            

        return None

    def cert_is_valid(self, hacienda_cer_path, ocsp_cer):
        return self.ocsp_response(self.ocsp(hacienda_cer_path, ocsp_cer))

    def key_match_cer(self):
        return self.get_info_cer()["modulus"] == self.key_modulus()

    @run
    def verify_ca(self, chain_cer_path):
        #command for generate chain certificate
        #cat ARC2_IES.pem AC2_SAT.pem ocsp.ac2_sat.pem > chain2.pem
        #print(self.files["cer"]["pem"])
        command = "openssl verify -CAfile {chain_cer} {user_cer}".format(
            chain_cer=chain_cer_path, 
            user_cer=self.files["cer"]["pem"])
        return command

    def is_valid_ca_cer(self, chain_cer_path):
        info = self.verify_ca(chain_cer_path).lower()
        if info.find("error") == -1 and info.find("ok") != -1:
            return True
        else:
            return False

    def clean(self, except_file=None):
        files = []
        except_files = set(["pkcs7"])
        if except_file is not None:
            except_files.add(except_file)
        for file_type in self.files:
            if isinstance(self.files[file_type], dict):
                for file_format, path in self.files[file_type].items():
                    if path is not None and file_format not in except_files:
                        files.append(path)
        clean(files)

    #@clean
    def sign(self, save_path, documento, password, issuer_cer_path, ocsp_cer, chain_cer):
        VALID_CERT = ["O=Servicio de Administraci\\xC3\\xB3n Tributaria", "O=Inmegen", "0=Test CA"]
        data_info = self.get_info_cer()
        error = self.key2pem(password)
        if error:
            self.clean()
            return error, "PEM", "La contraseña es incorrecta"
        if documento.user.curp != data_info["curp"]:
            self.clean()
            return "", "CURP", "El CURP del certificado no corresponde al registrado en el sistema"
        elif data_info["dateend"] < datetime.datetime.today():
            self.clean()
            return "", "SIGN", "El certificado ha expirado"
        elif not data_info["io"] in VALID_CERT:
            self.clean()
            return "", "SIGN", "El firmante del certificado no es válido"
        elif not self.key_match_cer():
            self.clean()
            return "", "SIGN", "El certificado no corresponde a la llave"
        elif not self.is_valid_ca_cer(chain_cer):
            self.clean()
            return "", "SIGN", "El certificado no corresponde a la cadena de certificados"
        #if not self.test: 
        elif not self.cert_is_valid(issuer_cer_path, ocsp_cer):
            self.clean()
            return "", "SIGN", "El certificado no es válido por el ocsp"
        
        self.sign_pkcs7(save_path, documento.xml.url)
        documento.xml_pkcs7 = self.files["sign"]["pkcs7"]
        try:
            certificado = Certificado.objects.get(fingerprint=data_info["fingerprint"])
        except Certificado.DoesNotExist: 
            certificado = Certificado.objects.create( 
                fingerprint=data_info["fingerprint"], 
                pem=self.get_value_from_file("cer", "pem"),
                user=documento.user) 
        documento.certificado = certificado
        documento.save()

    def get_ocsp_origin(self, file_type="der"):
        data_info = self.get_info_cer(file_type=file_type)
        _, serial = data_info["serial"].split("=")
        return serial[-17]

    def get_no_certificado(self, file_type="der"):
        data_info = self.get_info_cer(file_type=file_type)
        _, serial = data_info["serial"].split("=")
        return serial[1::2]

    @run
    def __verify(self, documento_url):
        print(self.files)
        command = "openssl smime -verify -in {pkcs7} -inform DER -content {file_check} -signer {cer} -noverify".format(
            pkcs7=self.files["sign"]["pkcs7"],
            cer=self.files["cer"]["pem"],
            file_check=documento_url
        )
        return command

    def verify(self, documento_url):
        return self.__verify(documento_url).find("Verification successful") != -1

    @run
    def xslt_xml_transform(self, xml_filename):
        self.files["sign"]["o_string"] = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        command = "xsltproc {} {} --noout --output {}".format(
            settings.XSLT, xml_filename, self.files["sign"]["o_string"])
        #print(command)
        return command

    def original_string(self, xml_filename):
        self.xslt_xml_transform(xml_filename)
        result = self.get_value_from_file("sign", "o_string")
        try:
            o_string = result[:2] + result[2:-2].replace("||", "") + result[-2:]
            with open(self.files["sign"]["o_string"], 'wb') as f:
                f.write(o_string)
        except ValueError:
            return None

    @run
    def digest_binary(self, original_string, out_digest_path):
        """return binary sign"""
        command = "openssl dgst -sha1 -out {sello} -sign {pem} {file_to_sign}".format( 
            sello=out_digest_path, 
            file_to_sign=original_string, 
            pem=self.files["key"]["pem"])
        return command

    def digest_hex(self, original_string):
        import hashlib
        with open(original_string, 'rb') as f:
            o_string = f.read()

        return hashlib.sha1(o_string).hexdigest()

    @run
    def base64(self, digest_path, out_base64_path):
        command = "openssl base64 -in {sello} -out {sello64}".format( 
            sello=digest_path, 
            sello64=out_base64_path)
        return command
        
    @run
    def get_pubkey(self):
        command = "openssl x509 -inform pem -in {cert} -pubkey -noout".format(
            cert=self.files["cer"]["pem"])
        return command

    @run
    def __dec(self, path_file_sello, base64):
        command = "openssl enc -base64 -d -in {base64} -out {sello}".format(
            base64=base64,
            sello=path_file_sello)
        return command

    @run
    def __verify_digest(self, path_file_sello, documento):
        command = "openssl dgst -sha1 -verify {pubkey} -signature {sello} {documento}".format(
            pubkey=self.files["cer"]["pubkey"],
            sello=path_file_sello,
            documento=documento)
        return command

    def verify_digest(self):
        pubkey = self.get_pubkey()
        self.files["cer"]["pubkey"] = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        self.files["sign"]["sello"] = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        with open(self.files["cer"]["pubkey"], "wb") as f:
            f.write(pubkey)

        self.__dec(self.files["sign"]["sello"], self.files["sign"]["base64"])
        return self.__verify_digest(
            self.files["sign"]["sello"], 
            self.files["sign"]["o_string"]).find("Verified OK") != -1

    def view_base64_sign(self):
        return self.get_value_from_file("sign", "base64")

    def get_value_from_file(self, name, type_data):
        with open(self.files[name][type_data], 'rb') as f:
            return f.read()


class CSD(DigitalSign):
    def __init__(self, *args, **kwargs):
        super(CSD, self).__init__(*args, **kwargs)
        self.files["sign"] = {"digest": None, "base64": None, "o_string": None, "sello": None}

    def sign(self, documento, password, issuer_cer_path, ocsp_cer, chain_cer):
        VALID_CERT = ["O=Servicio de Administraci\\xC3\\xB3n Tributaria", "O=Inmegen", "0=Test CA"]
        data_info = self.get_info_cer()
        error = self.key2pem(password)
        if error:
            self.clean()
            return error, "PEM", "La contraseña es incorrecta"
        elif not data_info["io"] in VALID_CERT:
            self.clean()
            return "", "SIGN", "El firmante del certificado no es válido"
        elif not self.key_match_cer():
            self.clean()
            return "", "SIGN", "El certificado no corresponde a la llave"
        #elif not self.is_valid_ca_cer(chain_cer):
        #    self.clean()
        #    return "", "SIGN", "El certificado no corresponde a la cadena de certificados"
        #elif not self.cert_is_valid(issuer_cer_path, ocsp_cer):
        #    self.clean()
        #    return "", "SIGN", "El certificado no es válido por el ocsp"

        self.files["sign"]["digest"] = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        self.files["sign"]["base64"] = tmp_dir_o_file+id_generator(size=SIZE_NAME)
        self.original_string(documento)
        self.digest_binary(self.files["sign"]["o_string"], self.files["sign"]["digest"])
        self.base64(self.files["sign"]["digest"], self.files["sign"]["base64"])

        #with open(self.files["sign"]["o_string"], 'rb') as f:
        #    print(f.read())

        #with open(self.files["sign"]["digest"], 'rb') as f:
        #    print(f.read())

        #with open(self.files["sign"]["base64"], 'rb') as f:
        #    return f.read()

class UserXMLData(object):
    def __init__(self, nombre_nomina, fecha_pago, folio, tz='America/Mexico_City'):
        self.data_template = {
            "total_neto": None,
            "fecha_emision": "",
            "sello": "",
            "no_certificado": "",
            "total_bruto": None,
            "folio": folio,
            "nombre_usuario": None,
            "rfc_usuario": None,
            "num_empleado": None,
            "nombre_nomina": nombre_nomina,
            "total_impuestos_retenidos": None,
            "curp": None,
            "tipo_regimen": "2",
            "fecha_pago": "",
            "fecha_inicial_pago": "",
            "fecha_final_pago": "",
            "num_dias_pagados": None,
            "departamento": None,
            "clabe": None,
            "puesto": None,
            "tipo_contrato": None,
            "periodicidad_pago": None,
            "percepcion_total_gravado": None,
            "percepcion_total_exento": 0.000000,
            "deduccion_total_gravado": 0.000000,
            "deduccion_total_exento": None,
            #"clave_presupuestal": None, ClavePresupuestal="{{ clave_presupuestal }}"
            "percepciones": [],
            "deducciones": [],
            "certificado": "",
            "prestamo_conteo": ""
        }
        self.fecha_pago = fecha_pago
        self.tz = pytz.timezone(tz)

    @property
    def curp(self):
        return self.data_template["curp"]

    @property
    def rfc(self):
        return self.data_template["rfc_usuario"]

    def add(self, field, value):
        self.data_template[field] = value

    def add_percepciones(self, value):
        self.data_template["percepciones"].append(value)

    def add_deducciones(self, value):
        self.data_template["deducciones"].append(value)

    def total_percepciones(self):
        return round(sum(percepcion["importe_gravado"] 
                for percepcion in self.data_template["percepciones"]), 2)

    def total_deducciones(self):
        return round(sum(deduccion["importe_gravado"] 
                for deduccion in self.data_template["deducciones"]), 2)

    def deducciones(self):
        return {deduccion["clave"]: deduccion for deduccion in self.data_template["deducciones"]}
                
    def transform_date(self):
        fecha_inicio, fecha_fin = self.data_template["fecha_pago"].split("AL")
        fecha_inicio = fecha_inicio.strip()
        fecha_fin = fecha_fin.strip()
        dd, mm, yyyy = fecha_inicio.split("/")
        fecha_inicio = datetime.date(int(yyyy), int(mm), int(dd)).strftime('%Y-%m-%d')
        fecha_fin = fecha_fin.strip()
        dd, mm, yyyy = fecha_fin.split("/")
        fecha_fin = datetime.date(int(yyyy), int(mm), int(dd)).strftime('%Y-%m-%d')
        self.add("fecha_inicial_pago", fecha_inicio)
        self.add("fecha_final_pago", fecha_fin)
        self.add("fecha_pago", self.fecha_pago)
        
    def transform2xml_signed(self, cer, key, password):
        from creacion_firma.utils import sign_xml
        xml_url = "/tmp/xml_sign.xml"
        self.add("fecha_emision", datetime.datetime.now(self.tz).strftime('%Y-%m-%dT%H:%M:%S'))
        xml = self.transform("plantilla_nomina.xml")
        with codecs.open(xml_url, "wb", "utf-8") as f:
            f.write(xml)
        sign_verify, sign_base64, no_certificado, certificado = sign_xml(
            xml_url, cer, key, password, type_ocsp="test")
        if sign_verify is True:
            print("OK")
            self.add("sello", sign_base64)
            self.add("no_certificado", no_certificado)
            self.add("certificado", certificado)
            return self.transform("plantilla_nomina.xml")
        else:
            print("Error de verificacion de sello")

    def transform(self, plantilla_url, compress=True):
        from creacion_firma.utils import transform_template2xml
        return transform_template2xml(plantilla_url, self.data_template, compress=compress)
