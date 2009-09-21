from django.conf.urls.defaults import *
from django.contrib import admin

from broadcastcms.base.models import ContentBase
from django.db.models import get_model

from views import *
from voting.views import xmlhttprequest_vote_on_object


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    
    url(r'account-links/$', account_links, name='account_links'),
    url(r'logout/$', logout, name='logout'),
    
    url(r'^admin/(.*)', admin.site.root),
    
    url(r'chart/(?P<slug>[\w-]+)??$', chart, name='chart'),
    
    url(r'competitions/$', competitions, name='competitions'),
    url(r'competitions/rules/$', competitions_rules, name='competitions_rules'),
    url(r'competitions/(?P<slug>[\w-]+)/$', competitions_content, name='competitions_content'),
    
    url(r'events/$', events, name='events'),
    url(r'events/(?P<slug>[\w-]+)/$', events_content, name='events_content'),
    
    url(r'galleries/$', galleries, name='galleries'),
    url(r'galleries/(?P<slug>[\w-]+)/$', galleries_content, name='galleries_content'),
   
    url(r'listen-live/$', listen_live, name='listen_live'),
    url(r'studio-cam/$', studio_cam, name='studio_cam'),
    
    url(r'news/$', news, name='news'),
    url(r'news/(?P<slug>[\w-]+)/$', news_content, name='news_content'),

    url(r'modals/content/(?P<slug>[\w-]+)/$', modals_content, name='modals_content'),
    url(r'modals/login/$', modals_login, name='modals_login'),
    url(r'modals/password_reset/$', modals_password_reset, name='modals_password_reset'),
    url(r'modals/register/$', modals_register, name='modals_register'),

    url(r'shows/line-up/(?P<day>[\w-]+)??$', shows_line_up, name='shows_line_up'),
    url(r'shows/(?P<slug>[\w-]+)/$', shows_dj_blog, name='shows_dj_blog'),
    url(r'shows/(?P<slug>[\w-]+)/profile/$', shows_dj_profile, name='shows_dj_profile'),
    url(r'shows/(?P<castmember_slug>[\w-]+)/(?P<content_slug>[\w-]+)/$', shows_dj_content, name='shows_dj_content'),

    url(r'validate/username/$', validate_username,  name='validate_username'),
    url(r'validate/captcha/$',  validate_captcha,   name='validate_captcha'),

    url(r'voting/(?P<slug>[\w-]+)/$', xmlhttprequest_vote_on_object, {'model': ContentBase, 'slug_field': 'slug', 'direction': 'up'}, name='xmlhttprequest_vote_on_object'),
)
