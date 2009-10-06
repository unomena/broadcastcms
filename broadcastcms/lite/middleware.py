from django.conf import settings

class URLSwitchMiddleware(object):
    def process_request(self, request):
        """
        Alters urlconf module used based on hostname, thus enabling the 
        delivery of different portals for desktop and mobile clients.
        TODO: Refactor to use DeviceAtlas or WURFL type device recognition 
        to determine switch
        """
        host = request.META['HTTP_HOST'].split(':')[0]
        if host in settings.DESKTOP_HOSTNAMES:
            settings.ROOT_URLCONF = 'broadcastcms.lite.desktop_urls'
        elif host in settings.MOBILE_HOSTNAMES:
            settings.ROOT_URLCONF = 'broadcastcms.lite.mobile_urls'
        return None