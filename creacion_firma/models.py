from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings

tmp_prefix = settings.TMP_DIR


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    curp = models.CharField(max_length=40, unique=True)
    number_user = models.PositiveIntegerField()
    token = models.CharField(max_length=120, unique=True, blank=True, null=True)

    def dinamic_token(self):
        from creacion_firma.utils import build_token
        self.token = build_token(self.curp, self.number_user)
        self.save()
        return self.token

    def __unicode__(self):
        return self.username


class Certificado(models.Model):
    user = models.ForeignKey(User)
    fingerprint = models.CharField(unique=True, max_length=255)
    pem = models.TextField()

    def __unicode__(self):
        return self.user.__unicode__()


class TransactionStatus(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10)
    number = models.CharField(max_length=20, blank=True, null=True)

    def dynamic_number(self):
        return self.fecha.strftime("%Y%m%d") + "_" + str(self.id)

    def __unicode__(self):
        return "%s [%s]" % (self.fecha.strftime("%Y%m%d%H%M%S"), self.status)


class NominaSubida(models.Model):
    nombre = models.CharField(max_length=50)
    visible = models.BooleanField(default=True)
    fecha = models.DateTimeField(auto_now_add=True)
    numero = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=(("ord", "Ordinaria"), ("ext", "Extraordinaria")))

    def serie_number(self):
        if self.numero is None:
            numero = ""
        else:
            numero = str(self.numero)

        return u"{nombre} {numero} {year} {tipo}".format(
            nombre=self.nombre, 
            numero=numero.zfill(2), 
            year=self.year, 
            tipo=self.tipo)

    def __unicode__(self):
        return self.serie_number()


class UserDocumentSign(models.Model):
    user = models.ForeignKey(User)
    nomina = models.ForeignKey(NominaSubida, blank=True, null=True)
    document = models.FileField()
    xml = models.FileField(storage=FileSystemStorage(location=tmp_prefix, base_url=''))
    xml_pkcs7 = models.FileField(blank=True, null=True, 
        storage=FileSystemStorage(location=tmp_prefix, base_url=''))
    digital_sign = models.TextField(blank=True, null=True)
    digital_sign_xml = models.TextField(blank=True, null=True)
    certificado = models.ForeignKey(Certificado, blank=True, null=True)
    transaction = models.ForeignKey(TransactionStatus)

    def document_name(self):
        return self.document.name.split("/").pop()

    def xml_name(self):
        return self.xml.name.split("/").pop()

    @property
    def nombre(self):
        return self.nomina.serie_number()

    def __unicode__(self):
        return self.xml_name()


class FirmarCertificado(models.Model):
    user = models.ForeignKey(User)
    req_file = models.FileField()
    certificado = models.FileField()

