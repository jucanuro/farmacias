# mi_farmacia_system/settings.py

from pathlib import Path
from datetime import timedelta # Necesario si en el futuro usas JWT, no hace daño tenerlo.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-mp^lw(i0ag12bm*4j+hnn@*mk4628+%3)2wp_ffnm24l%3m6c1"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken', # Usado para TokenAuthentication
    #'rest_framework_simplejwt', # Comentado, por lo tanto no se usa JWT

    'core',
    'inventario',
    'clientes',
    'proveedores',
    'compras',
    'ventas',
    'traslados',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'corsheaders.middleware.CorsMiddleware', # Debe estar lo más arriba posible
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "farmacias.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "farmacias.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "es-pe"

TIME_ZONE = "America/Lima"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/topics/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static", # Directorio para archivos estáticos de todo el proyecto
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Directorio donde se guardarán los archivos subidos por el usuario (ej. imágenes de productos)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Especifica tu modelo de usuario personalizado
AUTH_USER_MODEL = 'core.Usuario'

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', # Habilita la autenticación por Token
        'rest_framework.authentication.SessionAuthentication', # Permite la autenticación basada en sesión (útil para el navegador y el admin)
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', # Por defecto, todas las vistas requerirán autenticación
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend', # Permite el uso de filtros por defecto
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10 # Define el tamaño de la página para la paginación por defecto
}

# --- Configuración de CORS HEADERS ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # La URL de tu aplicación React
    "http://127.0.0.1:3000",
    # Añade aquí cualquier otra URL desde la que tu frontend pueda acceder
]

CORS_ALLOW_ALL_ORIGINS = False # Mejor especificar los orígenes permitidos

# *** ¡ESTAS LÍNEAS ERAN LAS QUE FALTABAN O ESTABAN INCOMPLETAS! ***
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization', # <-- ¡CRUCIAL! Permite que el encabezado Authorization sea enviado
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken', # Necesario si usas CSRF con sesión
    'x-requested-with',
]
CORS_ALLOW_CREDENTIALS = True # Permite que el navegador envíe cookies y encabezados de autenticación con peticiones cross-origin
# --- FIN Configuración de CORS HEADERS ---

