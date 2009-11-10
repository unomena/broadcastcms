import time
import urllib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import simplejson as json
from django.utils.hashcompat import md5_constructor


API_KEY = getattr(settings, "FACEBOOK_API_KEY", None)
API_SECRET = getattr(settings, "FACEBOOK_API_SECRET", None)


def facebook_signature(values, cookie_check=False):
    signature_keys = []
    
    _check_facebook_settings(API_KEY, API_SECRET)
    
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

    
def _check_facebook_settings(API_KEY, API_SECRET):
    message = "You must provide %s in your settings before using Facebook."
    if not API_KEY:
        raise ImproperlyConfigured(message % "FACEBOOK_API_KEY")
    if not API_SECRET:
        raise ImproperlyConfigured(message % "FACEBOOK_API_SECRET")


def facebook_api_request(method, **params):
    defaults = {
        "method": method,
        "api_key": API_KEY,
        "call_id": time.time(),
        "v": "1.0",
        "format": "json",
    }
    defaults.update(params)
    defaults["sig"] = facebook_signature(defaults)
    return json.load(urllib.urlopen(
        "http://api.facebook.com/restserver.php",
        urllib.urlencode(defaults),
    ))
