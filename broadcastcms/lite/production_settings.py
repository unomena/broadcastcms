from os import path
import sys

# Utility Constants
SCRIPT_PATH =  path.abspath(path.dirname(__file__))
BUILDOUT_PATH =  path.split(path.abspath(path.join(path.dirname(sys.argv[0]))))[0]

# Django settings for broadcastcmslite project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# If you set this to False, Django won't server static content (recommended)
SERVE_STATIC = False

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
MEDIA_ROOT = '%s/production_media/' % BUILDOUT_PATH

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
    'broadcastcms.lite.middleware.URLSwitchMiddleware',
)

ROOT_URLCONF = 'broadcastcms.lite.desktop_urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'broadcastcms.lite.context_processors.settings',
    'broadcastcms.lite.context_processors.section',
    'broadcastcms.lite.context_processors.site',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/templates' % SCRIPT_PATH,
)

AUTH_PROFILE_MODULE = "lite.UserProfile"

# Haystack globals
HAYSTACK_SITECONF = 'broadcastcms.lite.haystack_index'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = '%s/broadcastcms_index' % SCRIPT_PATH
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',

    'voting',
    'haystack',

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
                (55, 55),
                (188, 104),
            )
        },
    },
    'banner': {
        'ImageBanner': {
            'image': (
                (300, 250),
                (424, 260),
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
                (50, 50),
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
