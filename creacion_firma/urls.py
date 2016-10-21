from django.conf.urls import url
from creacion_firma import views as creacion_firma

urlpatterns = [
    url(r'^firmar/(?P<username>(\w+\.{0,1}\w*))/$', 
        creacion_firma.firmar, name="firmar"),
    url(r'^verificar/$', creacion_firma.verificar_lista_usuarios),
    url(r'^verificar/(?P<username>(\w+\.{0,1}\w*))/docs/$', 
        creacion_firma.verificar_docs_firmados, name="verificar_docs_firmados"),
    url(r'^verificar/admin/(?P<username>(\w+\.{0,1}\w*))/docs/$', 
        creacion_firma.verificar_docs_firmados_admin, 
        name="verificar_docs_firmados_admin"),
    url(r'^verificar/(?P<username>(\w+\.{0,1}\w*))/docs/(?P<doc_id>\d+)/$',
        creacion_firma.verificar_firma_doc, name="verificar_firma_doc"),
    url(r'^verificar/admin/(?P<username>(\w+\.{0,1}\w*))/docs/(?P<doc_id>\d+)/$',
        creacion_firma.verificar_firma_doc_admin, name="verificar_firma_doc_admin"),
    url(r'^bajar_certificado/(?P<cert_id>\d+)/$', 
        creacion_firma.bajar_certificado, name="bajar_certificado"),
    url(r'^documentos/(?P<username>(\w+\.{0,1}\w*))/(?P<token>\w+)/$', 
        creacion_firma.documentos, name="documentos"),
    url(r'^subir_nomina/$', creacion_firma.subir_nomina, name="subir_nomina"),
    url(r'^subir_nomina_xml/$', creacion_firma.subir_nomina_xml, 
        name="subir_nomina_xml"),
    url(r'^bajar_archivo/docs/(?P<doc_id>\d+)/type/(?P<type_doc>\w+)/$', 
        creacion_firma.bajar_archivo, name="bajar_archivo"),
    url(r'^resultados_subir_nomina/$', creacion_firma.resultados_subir_nomina, 
        name="resultados_subir_nomina"), 
    url(r'^login/$', creacion_firma.login, name="login"),
]
