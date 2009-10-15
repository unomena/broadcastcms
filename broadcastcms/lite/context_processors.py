from models import Settings
from broadcastcms.cache.decorators import cache_context_processor

def settings(request):
    """
    Get or create a lite settings object and add it to context['settings'].
    """
    settings = Settings.objects.get_or_create(pk='1')[0]
    return {'settings': settings}


def section(request):
    """
    Determines the current site section from request path and add it to context['section'].
    Section defaults to 'home'.
    """
    SECTIONS = ['home', 'shows', 'chart', 'competitions', 'news', 'events', 'galleries']
    path = request.path
    
    # remove starting '/' present
    if path.startswith('/'):
        path = path[1:]

    # section is determined by first path element, defaults to home
    path = path.split('/')
    section = path[0] if len(path) > 0 else 'home'
    section = section if section in SECTIONS else 'home'

    return {'section': section}
