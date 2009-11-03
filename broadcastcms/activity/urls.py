from django.conf.urls.defaults import *

import broadcastcms.activity.management


urlpatterns = patterns("broadcastcms.activity.views",
    url(r"^$", "my_activity", name="account_activity"),
    url(r"^friends/$", "friends_activity", name="account_friends_activity"),
)
