# based on http://nyquistrate.com/django/facebook-connect/

from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib import auth

from broadcastcms.facebook_integration.utils import (facebook_signature,
    facebook_api_request, API_KEY)
from broadcastcms.lite.models import UserProfile


class FacebookConnectMiddleware(object):
    
    def process_request(self, request):
        request.delete_facebook_cookies = False
        request.fb_authenticated = False
        
        if request.path.startswith(reverse("facebook_existing_user")):
            # allow this request to pass through
            return None
        
        if request.GET.get("fbc", False):
            request.delete_facebook_cookies = True
        
        if request.session.get("fb_signup_info"):
            # allow this request to pass through
            return None

        
        if not request.user.is_authenticated():
            if API_KEY in request.COOKIES:
                signature_hash = facebook_signature(request.COOKIES, True)
                if signature_hash == request.COOKIES[API_KEY]:
                    expiration = datetime.fromtimestamp(
                        float(request.COOKIES[API_KEY + "_expires"])
                    )
                    if expiration > datetime.now():
                        params = {
                            "uids": request.COOKIES[API_KEY + "_user"],
                            "fields": "profile_url,first_name,last_name",
                        }
                        result = facebook_api_request("users.getInfo", **params)
                        user_info = result[0]
                      
                        try:
                            queryset = UserProfile.objects.select_related(
                                "user"
                            ).filter(
                                facebook_id = user_info["uid"],
                            )
                            profile = queryset.get()
                        except UserProfile.DoesNotExist:
                            request.session["fb_signup_info"] = user_info
                            return HttpResponseRedirect(reverse("facebook_finish_signup_choice"))
                        else:
                            user = profile.user
                            user.backend = "django.contrib.auth.backends.ModelBackend"
                            auth.login(request, user)
                            # allow requests for ajax and session views
                            if request.path.startswith('/ajax') or request.path.startswith('/session'):
                                if API_KEY in request.COOKIES:
                                    # @@@ may need more checks before assuming this is true
                                    request.fb_authenticated = True
                                return None
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
        if hasattr(request, "delete_facebook_cookies") and request.delete_facebook_cookies:
            response.delete_cookie(API_KEY + "_user")
            response.delete_cookie(API_KEY + "_session_key")
            response.delete_cookie(API_KEY + "_expires")
            response.delete_cookie(API_KEY + "_ss")
            response.delete_cookie(API_KEY)
            response.delete_cookie("fbsetting_" + API_KEY)
        
        return response
