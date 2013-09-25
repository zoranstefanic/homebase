# Django settings for homebase project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import os
PROJECT_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(PROJECT_DIR,'media/samples')
EXPERIMENTS_DIR = os.path.join(PROJECT_DIR,'media/experiments')


# Registration stuff
ACCOUNT_ACTIVATION_DAYS = 7

ADMINS = (
    # ('Zoran Stefanic', 'zoran.stefanic@irb.hr'),
)

LOGIN_URL='/accounts/login/'
LOGIN_REDIRECT_URL='/profiles/edit'

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: "/profiles/%s/" % o.username
}

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_DIR,'homebase.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zagreb'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR,'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://localhost:8080/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/media/admin/'
STATIC_URL = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2nj=bp)x-)@)%lqvo6+$7oal@48g=hcou@@^i6_%lfd4dth^ag'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS =(
"django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.csrf",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
	'profiles.middleware.RequireLoginMiddleware',
)

#This imposes logins based on url scheme through RequireLoginMiddleware above
# Solution from http://stackoverflow.com/questions/2164069/best-way-to-make-djangos-login-required-the-default
LOGIN_REQUIRED_URLS = (
	r'/experiments/(.*)$',
#	r'(.*)$', Whole site requires login!!
)
LOGIN_REQUIRED_URLS_EXCEPTIONS = (
	r'/accounts/login(.*)$',
	r'/accounts/logout(.*)$',
	r'/media/(.*)$',
)


ROOT_URLCONF = 'homebase.urls'

AUTH_PROFILE_MODULE = 'profiles.Profile'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	'/home/zoran/django-projects/homebase/templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
	'django.contrib.webdesign',
	'django.contrib.admindocs',
    'django.contrib.admin',
    'django_extensions',
    'registration',
    'homebase.crysalis',
    'homebase.colors',
    'homebase.experiments',
    'homebase.samples',
    'homebase.schedule',
    'homebase.profiles',
)
