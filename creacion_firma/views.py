# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from subprocess import call, STDOUT, PIPE, Popen
from wsgiref.util import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from creacion_firma.models import UserDocumentSign, Certificado, User
from creacion_firma.models import TransactionStatus, NominaSubida
from creacion_firma.utils import id_generator, save_file, parse_info_cer, clean
from creacion_firma.classes import DigitalSign

import shlex
import logging
import zipfile
import StringIO
import datetime
import os

#from os.path import basename

tmp_prefix = settings.TMP_DIR
tmp_dir_o_file = tmp_prefix + "o_files/"
tmp_dir_pdf_file = tmp_prefix + "pdf_files/"
tmp_dir_xml_file = tmp_prefix + "xml_files/"
tmp_dir_pkcs7_file = tmp_prefix + "pkcs7_files/"
CA_DIR = "/var/www/CA/"
SIZE_NAME = 30

class StringFileWrapper(object):
    def __init__(self, data):
        self.data = data

    def readlines(self):
        return self.data

def logging_setup():
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger('key_service')
    hdlr = logging.FileHandler('/var/tmp/key_service.log')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.INFO)
    return logger

logger = logging_setup()


def control(function):
    def view(*args, **kwargs):
        #logger = logging.getLogger('key_service')
        request = args[0]
        error, type, msg, template, username = function(*args, **kwargs)
        if error:
            logger.info(type + ": " + error)
        elif type == "response" or type == "redirect":
            return msg
        if username == "":
            return redirect('https://inet.inmegen.gob.mx/')
        return render(request, template, {"msg": msg, "username": username, "token": "token"})
    return view

def token_check(function):
    def view(*args, **kwargs):
        request = args[0]
        try:
            user = User.objects.get(username=kwargs["username"])
            token = user.dinamic_token()
            if kwargs["token"] == token:
                user.token = token
                user.save()
                #user = User.objects.get(token=kwargs["token"])
                request.session["username"] = kwargs["username"]
                request.session["token"] = kwargs["token"]
            else:
                return redirect('https://inet.inmegen.gob.mx/')
        except User.DoesNotExist:
            return redirect('https://inet.inmegen.gob.mx/')
        return function(*args, **kwargs)
    return view

@control
def firmar(request, username):
    #logger = logging.getLogger('key_service')
    VALID_CERT = ["O=Servicio de Administraci\\xC3\\xB3n Tributaria", "O=Inmegen", "0=Test CA"]
    doc_key = "%s-documentos" % (username,)
    msg = "Documentos a firmar %s" % (len(request.session.get(doc_key, [])),)
    template = "crear_firma.html"
    token = request.session.get("token", '111')
    redirect_data = redirect('verificar_docs_firmados', username=username)
    logger = logging.getLogger('key_service')
    if len(request.session.get(doc_key, [])) == 0:
        return "", "redirect", redirect_data, "", ""

    if request.method == "POST":
        documentos = UserDocumentSign.objects.filter(
	    Q(id__in=request.session.get(doc_key, [])), 
            Q(digital_sign__isnull=True) | Q(digital_sign=''))

        try:
            cer = request.FILES["cer"]
        except MultiValueDictKeyError:
            return "empty file", "File", "Suba el certificado", template, username

        try:
            key = request.FILES["key"]
        except MultiValueDictKeyError:
            return "empty file", "File", "Suba el archivo key a firmar", template, username

        digital_sign = DigitalSign(cer=cer, key=key, test=settings.TEST_DS)
        password = request.POST["pass"]
        number = digital_sign.get_ocsp_origin()
        OCSP_NUMBER = "C"+number
        for documento in documentos:
            tmp_dir_pkcs7_file_date = tmp_dir_pkcs7_file+documento.transaction.number
            call(["mkdir", tmp_dir_pkcs7_file_date])     
            result = digital_sign.sign(
                tmp_dir_pkcs7_file_date, 
                documento, 
                password, 
                settings.CERTS[OCSP_NUMBER]["issuer"], 
                settings.CERTS[OCSP_NUMBER]["ocsp"], 
                settings.CERTS[OCSP_NUMBER]["chain"])
            
            if result is not None:
                return result[0], result[1], result[2], template, username

        digital_sign.clean()
        request.session.pop(doc_key, 0)
        return None, "redirect", redirect_data, template, username

    return None, None, msg, template, username


@login_required(login_url='/login/')
def verificar_lista_usuarios(request):
    from creacion_firma.forms import SelectYearForm, NominasFilterYear, FirmaOSinForm
    token = request.session.get("token", '123')
    username = request.session.get("username", '123')
    today = datetime.date.today()
    nomina = None
    if request.method == "POST":
        select_year = SelectYearForm(request.POST)
        firmado_form = FirmaOSinForm(request.POST)
        if select_year.is_valid() and firmado_form.is_valid():
            year = select_year.cleaned_data["year"]
            tipo = firmado_form.cleaned_data["tipo"]
            nominas_form = NominasFilterYear(request.POST, year=year)
            if nominas_form.is_valid():
                nomina = nominas_form.cleaned_data["nomina"]
        else:
            year = today.year
            tipo = "nf"
    else:
        year = today.year
        tipo = "nf"
        select_year = SelectYearForm(initial={"year": year})
        firmado_form = FirmaOSinForm(initial={"tipo": tipo})
        nominas_form = NominasFilterYear(year=year)

    if nomina is not None:
        if tipo == "nf":
            users_document_sign = UserDocumentSign.objects.filter(
                Q(nomina=nomina),
                Q(xml_pkcs7__isnull=True)|Q(xml_pkcs7='')).order_by("user__username")
        else:
            users_document_sign = UserDocumentSign.objects.filter(
                nomina=nomina,
                xml_pkcs7__isnull=False).exclude(xml_pkcs7='').order_by("user__username")
    else:
        users_document_sign = None
    
    return render(request, "verificar_lista_usuarios.html", {
        "users_document_sign": users_document_sign,
        "username": username,
        "token": token,
        "firmado_form": firmado_form,
        "select_year": select_year,
        "nominas_form": nominas_form})


def verificar_docs_firmados(request, username):
    from creacion_firma.forms import SelectYearForm

    token = request.session.get("token", '')
    today = datetime.date.today()
    if request.method == "POST":
        select_year = SelectYearForm(request.POST)
        if select_year.is_valid():
            year = select_year.cleaned_data["year"]
        else:
            year = today.year
    else:
        year = today.year
        select_year = SelectYearForm(initial={"year": year})

    documentos = UserDocumentSign.objects.filter(
        user__token=token, 
        xml_pkcs7__isnull=False,
        nomina__isnull=False,
        nomina__year=year).exclude(xml_pkcs7='').order_by(
        "-transaction__fecha", "-nomina__nombre")
    return render(request, "verificar_lista_docs.html", 
        {"documentos": documentos, "username": username, "token": token,
        "select_year": select_year})


@login_required(login_url='/login/')
def verificar_docs_firmados_admin(request, username):
    token = request.session.get("token", '')
    documentos = UserDocumentSign.objects.filter(user__username=username)
    return render(request, "verificar_lista_docs_admin.html", 
        {"documentos": documentos, "username": username, "token": token})


def documentos_check(documento, username, token):
    cer_pem = tmp_dir_o_file+id_generator(size=SIZE_NAME)
    if documento.certificado is not None:
        save_file(cer_pem, StringFileWrapper(documento.certificado.pem))
        digital_sign = DigitalSign(cer_pem=cer_pem)
        digital_sign.set_pkcs7(documento.xml_pkcs7.url)
        pkcs7_valid = digital_sign.verify(documento.xml.url)
        data_info = digital_sign.get_info_cer(file_type="pem")
        digital_sign.clean()
        clean([cer_pem])
    else:
        data_info = None
        pkcs7_valid = None

    return {
        "cert": data_info, 
        "username": username,
        "token": token,
        "documento": documento, 
        "pkcs7_valid": pkcs7_valid}


@login_required(login_url='/login/')
def verificar_firma_doc_admin(request, username, doc_id):
    token = request.session.get("token", '123')
    documento = UserDocumentSign.objects.get(user__username=username, id=doc_id)
    data = documentos_check(documento, username, token)
    return render(request, "verificar_firma.html", data)


def verificar_firma_doc(request, username, doc_id):
    token = request.session.get("token", '')
    documento = UserDocumentSign.objects.get(user__username=username, user__token=token, id=doc_id)
    data = documentos_check(documento, username, token)
    return render(request, "verificar_firma.html", data)


def bajar_certificado(request, cert_id):
    certificado = Certificado.objects.get(id=cert_id)

    path_file_cerpem = tmp_dir_o_file+id_generator(size=SIZE_NAME)
    path_file_cerder = tmp_dir_o_file+id_generator(size=SIZE_NAME)
    save_file(path_file_cerpem, StringFileWrapper(certificado.pem))

    command = "openssl x509 -in {pem} -inform PEM -out {der} -outform DER".format(
        pem=path_file_cerpem,
        der=path_file_cerder)
    proc = Popen(shlex.split(command), stderr=STDOUT, stdout=PIPE)
    error = proc.communicate()[0]
    if error:
        response = HttpResponse(error, content_type='text/plain')
    with open(path_file_cerder, "rb") as f:
        response = HttpResponse(FileWrapper(f), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=certificado-%s.cer' % (certificado.user.username,)

    return response


@token_check
def documentos(request, username, token):
    #### method for add a fake session ######
    #token = "37b00919308ca2c8fa752e41412d94f526ee34b9577dfbc1ae3a96faa76db9d6"
    #request.session["token"] = token
    #########################################
    documentos = (
        UserDocumentSign.objects.filter(
            user__token=token, 
            transaction__status="finished", 
            transaction__number__isnull=False,
            nomina__visible=True, 
            xml_pkcs7__isnull=True) |\
        UserDocumentSign.objects.filter(
            user__token=token, 
            transaction__status="finished", 
            transaction__number__isnull=False,
            nomina__visible=True,
            xml_pkcs7='')).order_by("nomina__nombre")
    doc_key = "%s-documentos" % (username,)
    if request.method == "POST":
        documentos_id = request.POST.getlist("documento")
        ids = [documento_id for documento_id in documentos_id]
        request.session[doc_key] = ids
        return redirect('firmar', username=username)
    else:
        if doc_key in request.session and len(request.session[doc_key]) > 0:
            msg = request.session[doc_key]
        else:
            msg = ""
    return render(request, "lista_documentos.html", {
        "documentos": documentos, 
        "msg": msg, 
        "username": username, 
        "token": token})


def login(request):
    from django.contrib.auth import authenticate, login
    from creacion_firma.forms import LoginForm

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["usuario"], 
                password=form.cleaned_data["password"])
            if not user is None and user.is_active:
                login(request, user)
                return HttpResponseRedirect(request.session.get('url', '/verificar/'))
    else:
        request.session['url'] = request.GET.get('next', '/verificar/')
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@login_required(login_url='/login/')
def subir_nomina_xml(request):
    from creacion_firma.forms import SubirNominaXMLForm
    from creacion_firma.utils import clean_dir, get_curp_xml_files
    from creacion_firma.utils import sync_user, unzip

    if request.method == "POST":
        form = SubirNominaXMLForm(request.POST, request.FILES)
        if form.is_valid():
            clean_dir(tmp_dir_xml_file+"tmp/")
            clean_dir(tmp_dir_xml_file+"tmp/timbrados/")

            transaction = TransactionStatus.objects.create(status="created")
            transaction.number = transaction.dynamic_number()
            if form.cleaned_data["anteriores"]:
                nomina_subida = form.cleaned_data["anteriores"]
                new_base_path_dir_xml = "%sT%s" % (tmp_dir_xml_file, "out_of_time")
            else:
                nomina_subida, _ = NominaSubida.objects.get_or_create(
                    nombre = form.cleaned_data["nombre"],
                    numero = form.cleaned_data["numero"],
                    year = form.cleaned_data["year"],
                    tipo = form.cleaned_data["tipo"])
                new_base_path_dir_xml = "%sT%s" % (tmp_dir_xml_file, transaction.number)
            
            try:
                zip_xml = form.cleaned_data['xml']
                unzip(tmp_dir_xml_file+"tmp/", zip_xml)
            except MultiValueDictKeyError:
                return "empty file", "File", "Suba el archivo a firmar", [], template, username

            curp_xml = get_curp_xml_files(tmp_dir_xml_file+"tmp/timbrados/")
            if not os.path.exists(new_base_path_dir_xml):
                os.makedirs(new_base_path_dir_xml)
            sin_curp_intranet = []
            for curp, xml_file in curp_xml:
                n_xml_file = new_base_path_dir_xml+"/"+id_generator(size=SIZE_NAME)
                try:
                    user = User.objects.get(curp=curp)
                except User.DoesNotExist:
                    user = sync_user(curp)

                if user == 0:
                    sin_curp_intranet.append(curp)
                elif user == -1:
                    sin_curp_intranet.append(curp + " Curp diferente en la intranet y el local")
                elif type(user) is type(int):
                    pass
                else:
                    try:
                        user_document_sign = UserDocumentSign.objects.get(
                            nomina=nomina_subida,
                            user=user)
                    except UserDocumentSign.DoesNotExist:
                        call(["mv", xml_file, n_xml_file])
                        UserDocumentSign.objects.create(
                            nomina=nomina_subida,
                            user=user,
                            transaction=transaction,
                            xml=n_xml_file)

            clean_dir(tmp_dir_xml_file+"tmp/")
            clean_dir(tmp_dir_xml_file+"tmp/timbrados/")
            transaction.status = "finished"
            transaction.save()
            request.session["sin_curp_intranet"] = sin_curp_intranet
            return HttpResponseRedirect(reverse('resultados_subir_nomina'))
    else:
        form = SubirNominaXMLForm()

    return render(request, "subir_nomina_xml.html", {"form": form})


@login_required(login_url='/login/')
def subir_nomina(request):
    from creacion_firma.forms import SubirNominaForm
    from creacion_firma.utils import split_nomina, link_pdf2curp, clean_dir
    from creacion_firma.utils import sync_user, unzip, search_xml_files
    from creacion_firma.utils import get_files_dir, get_curp2username

    if request.method == "POST":
        form = SubirNominaForm(request.POST, request.FILES)
        if form.is_valid():
            clean_dir(tmp_dir_pdf_file+"tmp/")
            clean_dir(tmp_dir_pdf_file+"tmp/pdfs/")
            clean_dir(tmp_dir_xml_file+"tmp/")
            clean_dir(tmp_dir_xml_file+"tmp/timbrados/")

            if form.cleaned_data["anteriores"]:
                nomina_subida = form.cleaned_data["anteriores"]
            else:
                nomina_subida, _ = NominaSubida.objects.get_or_create(
                    nombre = form.cleaned_data["nombre"],
                    numero = form.cleaned_data["numero"],
                    year = form.cleaned_data["year"],
                    tipo = form.cleaned_data["tipo"])
            try:
                zip_pdf = form.cleaned_data['pdf']
                unzip(tmp_dir_pdf_file+"tmp/", zip_pdf)
            except MultiValueDictKeyError:
                return "empty file", "File", "Suba el archivo a firmar", [], template, username

            try:
                zip_xml = form.cleaned_data['xml']
                unzip(tmp_dir_xml_file+"tmp/", zip_xml)
            except MultiValueDictKeyError:
                return "empty file", "File", "Suba el archivo a firmar", [], template, username

            transaction = TransactionStatus.objects.create(status="created")
            transaction.number = transaction.dynamic_number()
            new_base_path_dir_pdf = "%sT%s" % (tmp_dir_pdf_file, transaction.number)
            new_base_path_dir_xml = "%sT%s" % (tmp_dir_xml_file, transaction.number)
            num_files = 0
            pdf_files = get_files_dir(tmp_dir_pdf_file+"tmp/pdfs/")
            #call(["mkdir", tmp_dir_pdf_file+"tmp/split_pdfs/"])
            if not os.path.exists(tmp_dir_pdf_file+"tmp/split_pdfs/"):
                os.makedirs(tmp_dir_pdf_file+"tmp/split_pdfs/")
            for pdf_file in pdf_files:
                num_files += split_nomina(
                    tmp_dir_pdf_file+"tmp/split_pdfs/", 
                    tmp_dir_pdf_file+"tmp/pdfs/"+pdf_file,
                    init=num_files)
            files = link_pdf2curp(num_files, tmp_dir_pdf_file+"tmp/split_pdfs/")
            curp_pdf_xml, pdf_no_xml, xml_no_pdf = search_xml_files(files, 
                tmp_dir_xml_file+"tmp/timbrados/")
            #call(["mkdir", new_base_path_dir_pdf])
            if not os.path.exists(new_base_path_dir_pdf):
                os.makedirs(new_base_path_dir_pdf)
            #call(["mkdir", new_base_path_dir_xml])
            if not os.path.exists(new_base_path_dir_xml):
                os.makedirs(new_base_path_dir_xml)
            sin_curp_intranet = []
            for curp, pdf_file, xml_file in curp_pdf_xml:
                n_pdf_file = new_base_path_dir_pdf+"/"+id_generator(size=SIZE_NAME)
                n_xml_file = new_base_path_dir_xml+"/"+id_generator(size=SIZE_NAME)
                try:
                    user = User.objects.get(curp=curp)
                except User.DoesNotExist:
                    user = sync_user(curp)

                if user == 0:
                    sin_curp_intranet.append(curp)
                elif user == -1:
                    sin_curp_intranet.append(curp + " Curp diferente en la intranet y el local")
                elif type(user) is type(int):
                    pass
                else:
                    try:
                        UserDocumentSign.objects.get(
                            nomina=nomina_subida,
                            user=user)
                    except UserDocumentSign.DoesNotExist:
                        call(["mv", pdf_file, n_pdf_file])
                        call(["mv", xml_file, n_xml_file])
                        UserDocumentSign.objects.create(
                            nomina=nomina_subida,
                            user=user,
                            document=n_pdf_file,
                            transaction=transaction,
                            xml=n_xml_file)

            request.session["pdf_no_xml"] = get_curp2username(
                pdf_no_xml, sin_curp_intranet)

            request.session["xml_no_pdf"] = get_curp2username(
                xml_no_pdf, sin_curp_intranet)

            clean_dir(tmp_dir_pdf_file+"tmp/")
            clean_dir(tmp_dir_pdf_file+"tmp/pdfs/")
            clean_dir(tmp_dir_xml_file+"tmp/")
            clean_dir(tmp_dir_xml_file+"tmp/timbrados/")
            transaction.status = "finished"
            transaction.save()
            request.session["sin_curp_intranet"] = sin_curp_intranet
            return HttpResponseRedirect(reverse('resultados_subir_nomina'))
    else:
        form = SubirNominaForm()

    return render(request, "subir_nomina.html", {"form": form})


def bajar_archivo(request, doc_id, type_doc):
    if request.user.is_superuser or request.user.is_staff:
        documento = UserDocumentSign.objects.get(id=doc_id)
    else:
        token = request.session.get("token", '')
        documento = UserDocumentSign.objects.get(id=doc_id, user__token=token)

    if type_doc == "xml":
        with open(documento.xml.url, "r") as f:
            response = HttpResponse(FileWrapper(f), content_type="text/xml")
            response['Content-Disposition'] = 'attachment; filename=%s.%s' % (documento.nombre, "xml")
    elif type_doc == "pdf":
        from creacion_firma.xml2pdf import xml2pdf
        pdf = xml2pdf(documento.xml.url)
        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename=%s.%s' % (documento.nombre, "pdf")
        response.write(pdf)
    else:
        with open(documento.xml_pkcs7.url, "r") as f:
            response = HttpResponse(FileWrapper(f), content_type="application/bin")
            response['Content-Disposition'] = 'attachment; filename=%s.%s' % (documento.nombre, "p7")

    return response


def resultados_subir_nomina(request):
    if "pdf_no_xml" in request.session:
        pdf_no_xml = request.session["pdf_no_xml"]
    else:
        pdf_no_xml = []

    if "xml_no_pdf" in request.session:
        xml_no_pdf = request.session["xml_no_pdf"]
    else:
        xml_no_pdf = []

    if "sin_curp_intranet" in request.session:
        sin_curp_intranet = request.session["sin_curp_intranet"]
    else:
        sin_curp_intranet = []

    return render(request, "resultados_subir_nomina.html", {
        "pdf_no_xml": pdf_no_xml,
        "xml_no_pdf": xml_no_pdf,
        "sin_curp_intranet": sin_curp_intranet
        })


from creacion_firma.serializers import DigitalSignSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class DigitalSignAPI(APIView):
    
    def get(self, request, format=None):
        return Response({"status": "ok"})

    def post(self, request, format=None):
        serializer = DigitalSignSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            if result is True:
                return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
