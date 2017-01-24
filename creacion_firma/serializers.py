from rest_framework import serializers
from creacion_firma.classes import CSD
import io

def sign(password, cer, key, file_):
    from django.conf import settings
    import base64
    
    #password = "12345678"
    cer_f = io.BytesIO(base64.b64decode(cer))
    key_f = io.BytesIO(base64.b64decode(key))
    with open("/tmp/QNA.xml", 'wb') as f:
        f.write(base64.b64decode(file_))
    digital_sign = CSD(cer=cer_f, key=key_f, test=True)
    cer_f.close()
    key_f.close()
    print(digital_sign.get_info_cer()["o"])
    number = digital_sign.get_ocsp_origin()
    OCSP_NUMBER = "C"+number
    print(OCSP_NUMBER)
    info = digital_sign.sign(
        "/tmp/QNA.xml", 
        #"/home/agmartinez/csd_test/QNA.xml",
        password,
        settings.CERTS[OCSP_NUMBER]["issuer"],
        settings.CERTS[OCSP_NUMBER]["ocsp"],
        settings.CERTS[OCSP_NUMBER]["chain"])
    if info is not None:
        return info[2]
    print("SIGN: ", digital_sign.verify_digest())
    print("NoCertificado: ", digital_sign.get_no_certificado())
    print(digital_sign.digest_hex(digital_sign.files["sign"]["o_string"]))
    print("CLEAN")
    digital_sign.clean()


class DigitalSignSerializer(serializers.Serializer):
    passwd = serializers.CharField(required=True, allow_blank=False, max_length=100)
    cer = serializers.CharField(required=True, allow_blank=False, max_length=None)
    key = serializers.CharField(required=True, allow_blank=False, max_length=None)
    file = serializers.CharField(required=True, allow_blank=False, max_length=None)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        print("created")
        result = sign(validated_data.get("passwd", ""), validated_data.get("cer", ""), 
            validated_data.get("key", ""), validated_data.get("file", ""))
        if result is None:
            return True
        else:
            return result

    def validate(self, data):
        data = super(DigitalSignSerializer, self).validate(data)
        return data
