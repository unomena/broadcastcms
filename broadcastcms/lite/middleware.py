from django.conf import settings

class URLSwitchMiddleware(object):
    def process_request(self, request):
        """
        Alters urlconf module used based on hostname, thus enabling the 
        delivery of different portals for desktop and mobile clients.
        TODO: Refactor to use DeviceAtlas/WURFL device recognition 
        to determine switch
        Defaults to desktop urls when uncertain
        """
        # Default to desktop urls
        settings.ROOT_URLCONF = 'broadcastcms.lite.desktop_urls'

        # Grab the hostname from request.META
        meta = request.META
        if meta.has_key('HTTP_HOST'):
            host = request.META['HTTP_HOST']
        else:
            host = settings.DESKTOP_HOSTNAMES[0]
        
        # Switch urls based on hostname
        if host in settings.DESKTOP_HOSTNAMES:
            settings.ROOT_URLCONF = 'broadcastcms.lite.desktop_urls'
        elif host in settings.MOBILE_HOSTNAMES:
            settings.ROOT_URLCONF = 'broadcastcms.lite.mobile_urls'
