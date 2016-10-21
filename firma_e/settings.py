"""
Django settings for firma_e project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'creacion_firma',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

ROOT_URLCONF = 'firma_e.urls'

WSGI_APPLICATION = 'firma_e.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'es'
gettext = lambda s: s

LANGUAGES = (
    ('es', gettext('Spanish')),
    ('en', gettext('English')),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = BASE_DIR + '/static/'
STATIC_URL = '/static/'
MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_URL = '/media/'
TMP_DIR = '/home/agmartinez/Programas/firma_electronica/files/'
TEST_DS = True

MAGIC_NUMBER = 'HMFTEN&")!)#MWSUALG29b347cuhH#(Ndy=1N2'

CERTS = {"C0": 
            {"issuer": "/home/agmartinez/ocsp_3_uat/ac2_4096.pem", 
            "ocsp": "/home/agmartinez/ocsp_3_uat/OCSP_AC_4096_SHA256.pem",
            "chain": "/home/agmartinez/ocsp_3_uat/chain.pem"},
        "C2":
            {"issuer": "/home/agmartinez/ocsp_produccion/certificados/AC2_SAT.pem", 
            "ocsp": "/home/agmartinez/ocsp_produccion/certificados/ocsp.ac2_sat.pem",
            "chain": "/home/agmartinez/ocsp_produccion/certificados/chain2.pem"},
        "C3":
            {"issuer": "/home/agmartinez/ocsp_produccion/certificados/AC3_SAT.pem", 
            "ocsp": "/home/agmartinez/ocsp_produccion/certificados/ocsp.ac3_sat.pem",
            "chain": "/home/agmartinez/ocsp_produccion/certificados/chain3.pem"},
        "C4":
            {"issuer": "/home/agmartinez/ocsp_produccion/certificados/AC4_SAT.pem",
            "ocsp": "/home/agmartinez/ocsp_produccion/certificados/ocsp.ac4_sat.pem",
            "chain": "/home/agmartinez/ocsp_produccion/certificados/chain4.pem"}}

XSLT = "/home/agmartinez/csd_test/SF.CadenaOriginal/cadenaoriginal_3_2.xslt"

USER_CERTS_TEST = ["/home/agmartinez/ocsp_produccion/usuarios/mara800822jq4.pem", 
"/home/agmartinez/ocsp_produccion/usuarios/vasr820908s87.pem"]
