from django.conf import settings
from rest_framework import serializers
from creacion_firma.classes import GenericDigitalSign
from creacion_firma.utils import clean, id_generator
import io


def sign(password, cer, key, file_, test=True):
    from django.conf import settings
    import base64
    
    cer_f = io.BytesIO(base64.b64decode(cer))
    key_f = io.BytesIO(base64.b64decode(key))
    tmp_file = "/tmp/" + id_generator(size=30)
    with open(tmp_file, 'wb') as f:
        f.write(base64.b64decode(file_))
    digital_sign = GenericDigitalSign(cer=cer_f, key=key_f, test=test)
    cer_f.close()
    key_f.close()
    organization = digital_sign.get_info_cer()["o"]
    number = digital_sign.get_ocsp_origin()
    OCSP_NUMBER = "C"+number

    if test is True:
        OCSP_NUMBER = "C0"

    info = digital_sign.sign(
        tmp_file,
        password,
        settings.CERTS[OCSP_NUMBER]["issuer"],
        settings.CERTS[OCSP_NUMBER]["ocsp"],
        settings.CERTS[OCSP_NUMBER]["chain"])

    if info is not None:
        return {"status": "error", "msg": info[2]}

    #print("SIGN: ", digital_sign.verify_digest())
    no_cert = digital_sign.get_no_certificado()
    base64_sign = digital_sign.view_base64_sign()
    clean([tmp_file])
    digital_sign.clean()
    return {"status": "ok", "data": {"no_cert": no_cert, "base64": base64_sign, 
        "organization": organization}}


class DigitalSignSerializer(serializers.Serializer):
    passwd = serializers.CharField(required=True, allow_blank=False, max_length=100)
    cer = serializers.CharField(required=True, allow_blank=False, max_length=None)
    key = serializers.CharField(required=True, allow_blank=False, max_length=None)
    file = serializers.CharField(required=True, allow_blank=False, max_length=None)

    def create(self, validated_data):
        result = sign(validated_data.get("passwd", ""), validated_data.get("cer", ""), 
            validated_data.get("key", ""), validated_data.get("file", ""),  test=settings.DEBUG)
        return result

    def validate(self, data):
        data = super(DigitalSignSerializer, self).validate(data)
        return data
