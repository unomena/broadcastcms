from django.conf import settings

class URLSwitchMiddleware(object):
    def process_request(self, request):
        """
        Alters urlconf module used based on hostname, thus enabling the 
        delivery of different portals for different clients, i.e desktop and mobile clients.
        TODO: Refactor to use DeviceAtlas/WURFL device recognition to determine switch.
        """
        # grab url switches from settings. 
        # don't do anything if no switches are found
        url_switches = getattr(settings, 'URL_SWITCHES', None)
        if not url_switches:
            return

        # grab the hostname from request.META
        # don't do anything if no hostname is found
        meta = request.META
        if meta.has_key('HTTP_HOST'):
            host = request.META['HTTP_HOST']
        else:
            return
      
        # only change urlconf if a valid switch is found
        if url_switches.has_key(host):
            request.urlconf = url_switches[host]
