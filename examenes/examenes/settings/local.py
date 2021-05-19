from .base import *
import firebase_admin
from firebase_admin import credentials

with open("secret.json") as f:
    secret = json.loads(f.read())

def get_secret(secret_name,secrets = secret):
    try:
        return secrets[secret_name]
    except:
        msg= "La variable %s no existe" % secret_name
        raise ImproperlyConfigured(msg)


SECRET_KEY = get_secret("SECRET_KEY")


DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret("DB_NAME"),
        'USER': get_secret("USER"),
        'PASSWORD': get_secret("PASSWORD"),
        'HOST': 'localhost',
        'PORT': '5432'
        
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",

]

MEDIA_URL = '/media/'

cred = credentials.Certificate("accountkey.json")
firebase_admin.initialize_app(cred)