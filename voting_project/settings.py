"""
Django settings for voting_project project.
"""
import os
from pathlib import Path
import dj_database_url
from decouple import config # Esta librería nos ayuda a leer claves secretas sin escribirlas en el código

# Construye rutas dentro del proyecto (ej: BASE_DIR / 'subdir').
BASE_DIR = Path(__file__).resolve().parent.parent


# --- CONFIGURACIÓN DE SEGURIDAD ---

# SECURITY WARNING: keep the secret key used in production secret!
# Aquí le decimos: "Intenta leer la clave secreta de un archivo oculto (.env), si no la encuentras, usa esta por defecto".
SECRET_KEY = config('SECRET_KEY', default='django-insecure-7o*ei85ff72s6$9cv55(a2(bm+-v43rc7ue##)7vq8(+igw=8=')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True nos muestra errores detallados (útil programando). 
# DEBUG = False oculta errores al usuario (obligatorio en producción).
DEBUG = config('DEBUG', default=True, cast=bool)

# Aquí definimos qué dominios pueden servir esta página. '*' significa que cualquiera puede (necesario para Render).
ALLOWED_HOSTS = ['*']


# --- APLICACIONES INSTALADAS ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # --- Mi Aplicación ---
    # Aquí registramos la app 'voting' para que Django sepa que existe y cargue sus modelos/vistas.
    'voting', 
]

MIDDLEWARE = [
    # AÑADIDO: WhiteNoise ayuda a que que la página sirva los estilos (CSS) e imágenes correctamente cuando se suba a internet.
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'voting_project.urls' # Archivo principal de rutas

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Aquí le decimos a Django que busque archivos HTML en la carpeta 'templates' en la raíz.
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'voting_project.wsgi.application'


# --- BASE DE DATOS ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        # Esta lógica es muy útil:
        # 1. Si estamos en internet (Render), busca una base de datos real (PostgreSQL).
        # 2. Si estamos en tu compu, usa el archivo local 'db.sqlite3'.
        default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3'),
        conn_max_age=600 # Mantiene la conexión viva un rato para ir más rápido
    )
}


# Password validation
# Validaciones automáticas para que las contraseñas no sean "12345".
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# --- IDIOMA Y ZONA HORARIA ---
LANGUAGE_CODE = 'es-mx'        # Pone los mensajes de error y admin en Español de México
TIME_ZONE = 'America/Mexico_City' # Ajusta la hora a CDMX
USE_I18N = True
USE_TZ = False # Si es False, guarda la hora tal cual es en México (sin conversión UTC estricta)


# --- ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES) ---
# URL base para acceder a los estáticos (ej: misitio.com/static/estilo.css)
STATIC_URL = 'static/'

# Carpeta donde Django juntará TODOS los archivos estáticos antes de subir el sitio (comando collectstatic).
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Carpetas donde Django busca archivos estáticos mientras desarrollas.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- REDIRECCIÓN ---
# Cuando el usuario se loguea correctamente, lo mandamos directo a la guía.
LOGIN_REDIRECT_URL = '/voting/guia/'
# Si alguien intenta entrar a una zona privada sin permiso, lo mandamos aquí.
LOGIN_URL = '/login/'


# ... al final de settings.py
# --- Configuración de Enlaces Externos ---
# Variable global para tener el link de la repo a mano en cualquier parte.
GITHUB_REPO_URL = "https://github.com/LilianaVo/Proyecto"