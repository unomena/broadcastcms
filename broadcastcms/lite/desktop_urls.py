from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

from broadcastcms.base.models import ContentBase
import broadcastcms.lite.management

from desktop_views import *
from voting.views import xmlhttprequest_vote_on_object

admin.autodiscover()

handler404 = 'broadcastcms.lite.desktop_views.handler404'
handler500 = 'broadcastcms.lite.desktop_views.handler500'

messages_urls = patterns('user_messages.views',
    url(r'^inbox/$', 'inbox',
        {'template_name': 'desktop/content/account/messages/inbox.html'},
        name='messages_inbox'),
    url(r'^create/$', 'message_create',
        {'template_name': 'desktop/content/account/messages/create.html', 'multiple': True},
        name='message_create'),
    url(r'^create/(?P<user_id>\d+)/$', 'message_create',
        {'template_name': 'desktop/content/account/messages/create.html', 'multiple': True},
        name='message_create'),
    url(r'^thread/(?P<thread_id>\d+)/$', 'thread_detail',
        {'template_name': 'desktop/content/account/messages/thread_detail.html'},
        name='messages_thread_detail'),
    url(r'^thread/(?P<thread_id>\d+)/delete/$', 'thread_delete',
        name='messages_thread_delete'),
)

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    
    url(r'^facebook/', include('broadcastcms.facebook_integration.urls')),
    
    url(r'account-links/$', account_links, name='account_links'),
    url(r'logout/$', logout, name='logout'),
    url(r'comment-add/$', comment_add, name='comment_add'),
    
    url(r'^admin/(.*)', admin.site.root),
    
    url(r'^account/picture/$', account_picture, name='account_picture'),
    url(r'^account/profile/$', account_profile, name='account_profile'),
    url(r'^account/subscriptions/$', account_subscriptions, name='account_subscriptions'),
    url(r'^account/friends/$', account_friends, name='account_friends'),
    url(r'^account/friends/find/$', account_friends_find, name='account_friends_find'),
    url(r'^account/friends/response/(\d+)/$', 'friends.views.respond_to_friendship_invitation', {'redirect_to_view': 'account_friends'}, name='account_friends_reply'),
    url(r'^account/messages/', include(messages_urls)),
    url(r'^account/history/$', include("broadcastcms.history.urls")),
    
    url(r'chart/$', ChartView(), name='chart'),
    
    url(r'competitions/$', competitions, name='competitions'),
    url(r'competitions/rules/$', competitions_rules, name='competitions_rules'),
    url(r'competitions/(?P<slug>[\w-]+)/$', competitions_content, name='competitions_content'),
    
    url(r'contact/$', contact, name='contact'),
    
    url(r'events/$', events, name='events'),
    url(r'events/(?P<slug>[\w-]+)/$', events_content, name='events_content'),
    
    url(r'galleries/$', galleries, name='galleries'),
    url(r'galleries/(?P<slug>[\w-]+)/$', galleries_content, name='galleries_content'),
   
    url(r'info/(?P<section>[\w-]+)/$', info_content, name='info_content'),
    
    url(r'listen-live/$', listen_live, name='listen_live'),
    url(r'studio-cam/$', studio_cam, name='studio_cam'),
    
    url(r'news/$', news, name='news'),
    url(r'news/(?P<slug>[\w-]+)/$', news_content, name='news_content'),

    url(r'modals/content/(?P<slug>[\w-]+)/$', modals_content, name='modals_content'),
    url(r'modals/login/$', modals_login, name='modals_login'),
    url(r'modals/password_reset/$', modals_password_reset, name='modals_password_reset'),
    url(r'modals/register/$', modals_register, name='modals_register'),

    url(r'shows/line-up/$', shows_line_up, name='shows_line_up'),
    url(r'shows/(?P<slug>[\w-]+)/$', shows_dj_blog, name='shows_dj_blog'),
    url(r'shows/(?P<slug>[\w-]+)/profile/$', shows_dj_profile, name='shows_dj_profile'),
    url(r'shows/(?P<castmember_slug>[\w-]+)/(?P<content_slug>[\w-]+)/$', shows_dj_content, name='shows_dj_content'),

    url(r'search-results/$', search_results, name='search_results'),
    
    url(r'validate/captcha/$',  validate_captcha,   name='validate_captcha'),
    url(r'validate/password/$', validate_password,  name='validate_password'),
    url(r'validate/password-confirm/$', validate_password_confirm,  name='validate_password_confirm'),
    url(r'validate/username/$', validate_username,  name='validate_username'),

    url(r'voting/(?P<slug>[\w-]+)/$', xmlhttprequest_vote_on_object, {'model': ContentBase, 'slug_field': 'slug', 'direction': 'up'}, name='xmlhttprequest_vote_on_object'),

    url(r'(?P<pk>[\w-]+)/$', short_redirect,  name='short_redirect'),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
