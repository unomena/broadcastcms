from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from broadcastcms import public
from broadcastcms.show.models import Show, CastMember


class CastMemberViews(object):
    def get_absolute_url(self):
        return reverse('shows_dj_blog', kwargs={'slug': self.slug})

public.site.register(CastMember, CastMemberViews)
