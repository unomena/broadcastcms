from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r'^xd-receiver/$', direct_to_template, {
        "template": "desktop/facebook_integration/xd_receiver.html",
    }, name="facebook_xd_receiver"),
    url(r'^success/$', direct_to_template, {
        "template": "desktop/facebook_integration/success.html",
    }, name="facebook_success_login"),
)

urlpatterns += patterns("broadcastcms.facebook_integration.views",
    url(r'^finish_signup/$', "finish_signup", name="facebook_finish_signup"),
)
