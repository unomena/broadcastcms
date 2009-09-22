from os import path
import sys

# Utility Constants
BUILDOUT_PATH =  path.split(path.abspath(path.join(path.dirname(sys.argv[0]))))[0]

# Django settings for broadcastcmslite project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Africa/Johannesburg'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%s/media/' % BUILDOUT_PATH

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x5#t3)+2mg_jgx%8gw-s^8ogv_^=u#!d%de6%)9-&rxg6x9jf@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'broadcastcms.lite.production_urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'broadcastcms.lite.context_processors.settings',
    'broadcastcms.lite.context_processors.section',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

AUTH_PROFILE_MODULE = "lite.UserProfile"

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'voting',

    'broadcastcms.banner',
    'broadcastcms.base',
    'broadcastcms.calendar',
    'broadcastcms.competition',
    'broadcastcms.gallery',
    'broadcastcms.event',
    'broadcastcms.label',
    'broadcastcms.post',
    'broadcastcms.public',
    'broadcastcms.radio',
    'broadcastcms.scaledimage',
    'broadcastcms.show',
    'broadcastcms.chart',
    'broadcastcms.lite',
)

IMAGE_SCALES = {
    'base': {
        'ContentBase': {
            'image': (
                (80, 46), 
                (107, 60), 
                (424, 260),
            )
        },
    },
    'banner': {
        'ImageBanner': {
            'image': (
                (300, 250),
            )
        },
    },
    'competition': {
        'Competition': {
            'image': (
                (107, 60), 
            )
        },
    },
    'gallery': {
        'Gallery': {
            'image': (
                (188, 104),
            )
        },
        'GalleryImage': {
            'image': (
                (80, 53),
            )
        },
    },
    'lite': {
        'UserProfile': {
            'image': (
                (33, 33), 
                (41, 41),
            )
        }
    },
    'radio': {
        'Song': {
            'image': (
                (89, 50),
            )
        },
    },
    'show': {
        'Show': {
            'image': (
                (216, 77), 
                (188, 104),
            )
        },
        'CastMember': {
            'image': (
                (81, 81), 
                (193, 109), 
            )
        },
    },
}
