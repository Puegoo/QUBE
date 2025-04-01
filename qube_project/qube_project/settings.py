from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6nwx9j5+=kalnxn&a((ed-b5o41!mjb*#i$*48#uje0(dbs^oa'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # 'django.contrib.admin',
    # Usuwamy lub komentujemy django.contrib.auth oraz contenttypes, aby nie używać wbudowanego modelu użytkownika
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'qube',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Usuwamy AuthenticationMiddleware
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qube_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # Usuwamy kontekst auth
                # 'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'qube.context_processors.neo4j_user',
            ],
        },
    },
]

MIGRATION_MODULES = {
    'auth': None,
    'contenttypes': None,
    'admin': None,
}

WSGI_APPLICATION = 'qube_project.wsgi.application'

# Wyłączamy bazę danych – sesje będą przechowywane np. w ciasteczkach
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Ustawiamy sesje na ciasteczka, aby nie korzystać z bazy
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Konfiguracja Neo4j
NEOMODEL_NEO4J_BOLT_URL = "bolt://neo4j:qube12345@localhost:7687"
NEOMODEL_SIGNALS = False
NEOMODEL_ENCRYPTED_CONNECTION = False