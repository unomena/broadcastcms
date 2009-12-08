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
    url(r'^finish-signup-choice/$', "finish_signup_choice", name="facebook_finish_signup_choice"),
    url(r'^finish-signup-new/$', "finish_signup_new", name="facebook_finish_signup_new"),
    url(r'^finish-signup-existing/$', "finish_signup_existing", name="facebook_finish_signup_existing"),
    url(r'^permissions/$', "permissions", name="facebook_permissions"),
    url(r'^existing_user/$', "existing_user", name="facebook_existing_user"),
)
