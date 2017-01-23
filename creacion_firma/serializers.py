from rest_framework import serializers
from creacion_firma.classes import CSD
import io

def sign(password, cer, key):
    from django.conf import settings
    import base64
    
    #password = "12345678"
    cer_f = io.BytesIO(base64.b64decode(cer))
    key_f = io.BytesIO(base64.b64decode(key))
    digital_sign = CSD(cer=cer_f, key=key_f, test=True)
    cer_f.close()
    key_f.close()
    print(digital_sign.get_info_cer()["o"])
    number = digital_sign.get_ocsp_origin()
    OCSP_NUMBER = "C"+number
    print(OCSP_NUMBER)
    info = digital_sign.sign(
        "/home/agmartinez/csd_test/QNA.xml", 
        password,
        settings.CERTS[OCSP_NUMBER]["issuer"],
        settings.CERTS[OCSP_NUMBER]["ocsp"],
        settings.CERTS[OCSP_NUMBER]["chain"])
    if info is not None:
        return info[2]
    #print("SIGN: ", digital_sign.verify_digest())
    #print("NoCertificado: ", digital_sign.get_no_certificado())
    #print(digital_sign.digest_hex(digital_sign.files["sign"]["o_string"]))
    print("CLEAN")
    digital_sign.clean()


class DigitalFirmSerializer(serializers.Serializer):
    passwd = serializers.CharField(required=True, allow_blank=False, max_length=100)
    cer = serializers.CharField(required=True, allow_blank=False, max_length=None)
    key = serializers.CharField(required=True, allow_blank=False, max_length=None)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        print("created")
        result = sign(validated_data.get("passwd", ""), validated_data.get("cer", ""), 
            validated_data.get("key", ""))
        if result is None:
            return True
        else:
            return result

    def validate(self, data):
        data = super(DigitalFirmSerializer, self).validate(data)
        return data
    #def update(self, instance, validated_data):
    #    """
    #    Update and return an existing `Snippet` instance, given the validated data.
    #    """
    #    instance.title = validated_data.get('title', instance.title)
    #    instance.code = validated_data.get('code', instance.code)
    #    instance.linenos = validated_data.get('linenos', instance.linenos)
    #    instance.language = validated_data.get('language', instance.language)
    #    instance.style = validated_data.get('style', instance.style)
    #    instance.save()
    #    return instance
