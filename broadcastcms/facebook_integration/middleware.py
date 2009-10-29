# based on http://nyquistrate.com/django/facebook-connect/

import time
import urllib

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.hashcompat import md5_constructor
from django.utils import simplejson as json

from django.contrib import auth

from broadcastcms.lite.models import UserProfile


class FacebookConnectMiddleware(object):
    
    def process_request(self, request):
        API_KEY = settings.FACEBOOK_API_KEY
        
        request.delete_facebook_cookies = False
        request.fb_authenticated = False
        
        if request.GET.get("fbc", False):
            request.delete_facebook_cookies = True
        
        if request.session.get("fb_signup_info"):
            # allow this request to pass through
            return None
        
        if not request.user.is_authenticated():
            if API_KEY in request.COOKIES:
                signature_hash = self.facebook_signature(request.COOKIES, True)
                if signature_hash == request.COOKIES[API_KEY]:
                    expiration = datetime.fromtimestamp(
                        float(request.COOKIES[API_KEY + "_expires"])
                    )
                    if expiration > datetime.now():
                        params = {
                            "method": "users.getInfo",
                            "api_key": API_KEY,
                            "call_id": time.time(),
                            "v": "1.0",
                            "uids": request.COOKIES[API_KEY + "_user"],
                            "fields": "profile_url,first_name,last_name",
                            "format": "json",
                        }
                        params["sig"] = self.facebook_signature(params)
                        result = json.load(urllib.urlopen(
                            "http://api.facebook.com/restserver.php",
                            urllib.urlencode(params),
                        ))
                        user_info = result[0]
                        
                        try:
                            queryset = UserProfile.objects.select_related(
                                "user"
                            ).filter(
                                facebook_url = user_info["profile_url"],
                            )
                            profile = queryset.get()
                        except UserProfile.DoesNotExist:
                            request.session["fb_signup_info"] = user_info
                            return HttpResponseRedirect(reverse("facebook_finish_signup"))
                        else:
                            user = profile.user
                            user.backend = "django.contrib.auth.backends.ModelBackend"
                            auth.login(request, user)
                            return HttpResponseRedirect(reverse("home"))
                    else:
                        request.delete_facebook_cookies = True
                        return HttpResponse("expired")
                else:
                    request.delete_facebook_cookies = True
                    return HttpResponse("%s != %s" % (signature_hash, request.COOKIES[API_KEY]))
            else:
                # nothing to worry about in this case
                pass
        else:
            if API_KEY in request.COOKIES:
                # @@@ may need more checks before assuming this is true
                request.fb_authenticated = True
    
    def process_response(self, request, response):
        API_KEY = settings.FACEBOOK_API_KEY
        
        if hasattr(request, "delete_facebook_cookies") and request.delete_facebook_cookies:
            response.delete_cookie(API_KEY + "_user")
            response.delete_cookie(API_KEY + "_session_key")
            response.delete_cookie(API_KEY + "_expires")
            response.delete_cookie(API_KEY + "_ss")
            response.delete_cookie(API_KEY)
            response.delete_cookie("fbsetting_" + API_KEY)
        
        return response
    
    def facebook_signature(self, values, cookie_check=False):
        API_KEY = settings.FACEBOOK_API_KEY
        API_SECRET = settings.FACEBOOK_API_SECRET
        signature_keys = []
        
        for key in sorted(values.keys()):
            if cookie_check:
                if key.startswith("%s_" % API_KEY):
                    signature_keys.append(key)
            else:
                signature_keys.append(key)
        
        signature = []
        for key in signature_keys:
            if cookie_check:
                k = key.replace("%s_" % API_KEY, "")
                signature.append("%s=%s" % (k, values[key]))
            else:
                signature.append("%s=%s" % (key, values[key]))
        signature.append(API_SECRET)
        
        return md5_constructor("".join(signature)).hexdigest()
