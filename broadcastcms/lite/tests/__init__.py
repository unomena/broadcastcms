import os
from windmill.authoring import djangotest
 
#from django.test import *
 
from broadcastcms.lite.tests.context_processors import *
from broadcastcms.lite.tests.desktop_inclusion_tags import *
from broadcastcms.lite.tests.desktop_views import *
from broadcastcms.lite.tests.middleware import *
from broadcastcms.lite.tests.models import *
 
 
# Windmill test hook running each test seperately, see
# http://www.rfk.id.au/blog/entry/django-unittest-windmill-goodness
# For the default Windmill test hook see
# http://trac.getwindmill.com/wiki/WindmillAndDjango
choice = raw_input('Do you want to run Windmill tests? y/n: ').lower()
if choice == 'y':
    wmtests = os.path.join(os.path.dirname(os.path.abspath(__file__)),"windmill")
    for nm in os.listdir(wmtests):
        if nm.startswith("test") and nm.endswith(".py"):
            testnm = nm[:-3]
            class WindmillTest(djangotest.WindmillDjangoUnitTest):
                test_dir = os.path.join(wmtests,nm)
                browser = "firefox"
            WindmillTest.__name__ = testnm
            globals()[testnm] = WindmillTest
            del WindmillTest 
