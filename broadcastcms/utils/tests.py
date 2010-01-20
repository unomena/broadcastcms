from django.http import HttpResponseBadRequest
from django.test import TestCase

from broadcastcms.test.mocks import RequestFactory

from decorators import ajax_required

class DecoratorsTestCase(TestCase):
    def testAjaxRequired(self):
        @ajax_required
        def dummyFunction(request):
            return 'valid response'
        
        # on non ajax request return HttpResponseBadRequest
        request = RequestFactory().get('/')
        result = dummyFunction(request)
        self.failUnless(isinstance(result, HttpResponseBadRequest))
        
        # on ajax request don't return HttpResponseBadRequest
        request = RequestFactory().get('/')
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        result = dummyFunction(request)
        self.failUnless(result == 'valid response')
