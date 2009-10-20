from django.contrib.sites.models import Site

from broadcastcms.cache.decorators import cache_context_processor
from broadcastcms.lite.models import Settings

SITE_SECTIONS = ['home', 'shows', 'chart', 'competitions', 'news', 'events', 'galleries']

def settings(request):
    """
    Get or create a lite settings object and add it to context['settings'].
    """
    settings = Settings.objects.get_or_create(pk='1')[0]
    return {'settings': settings}


def section(request):
    """
    Determines the current site section from request path and adds
    it to context['section']. Section defaults to 'home'.
    """
    path = request.path
    
    # remove starting '/' present
    if path.startswith('/'):
        path = path[1:]

    # section is determined by first path element, defaults to home
    path = path.split('/')
    section = path[0] if len(path) > 0 else 'home'
    section = section if section in SITE_SECTIONS else 'home'

    return {'section': section}


def site(request):
    """
    Get current site and add its name and domain to context['site_name']
    and context['site_domain'] respectively.
    """
    site_info = {}
    if Site._meta.installed:
        site = Site.objects.get_current()
        site_info['site_domain'] = site.domain
        site_info['site_name'] = site.name
    return site_info
