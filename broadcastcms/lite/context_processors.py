from models import Settings
from broadcastcms.cache.decorators import cache_context_processor

@cache_context_processor(60*10)
def settings(request):
    settings = Settings.objects.all()
    if len(settings): settings = settings[0]
    else: settings = Settings.objects.create()
    return {'settings': settings}


def section(request):
    SECTIONS = ['home', 'shows', 'chart', 'competitions', 'news', 'events', 'galleries']
    path = request.path.split('/')
    section = path[1] if len(path) > 1 else 'home'
    section = section if section in SECTIONS else 'home'
    return {'section': section}
