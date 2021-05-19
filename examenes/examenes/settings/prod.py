
from .base import *
import firebase_admin
from firebase_admin import credentials
import os

DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret("DB_NAME"),
        'USER': get_secret("USER"),
        'PASSWORD': get_secret("PASSWORD"),
        'HOST': '/tmp/',
        'PORT': '5432'
        
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR,'static')

MEDIA_ROOT = os.path.join(BASE_DIR,'media')
MEDIA_URL = '/media/'

cred = credentials.Certificate("/home/bitnami/projects/evaluaciones-site/examenes/accountkey.json")
firebase_admin.initialize_app(cred)
