from django.conf.urls.defaults import *

import broadcastcms.history.management


urlpatterns = patterns("broadcastcms.history.views",
    url(r"^$", "my_history", name="account_history"),
    url(r"^friends/$", "friends_history", name="account_friends_history"),
)
