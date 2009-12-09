from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

from broadcastcms.base.models import ContentBase
import broadcastcms.lite.management
from broadcastcms.lite.forms import NewMessageFormMultipleFriends

from desktop_views import *
from voting.views import xmlhttprequest_vote_on_object

admin.autodiscover()

handler404 = 'broadcastcms.lite.desktop_views.handler404'
handler500 = 'broadcastcms.lite.desktop_views.handler500'

messages_urls = patterns('user_messages.views',
    #url(r'^inbox/$', 'inbox',
    #   {'template_name': 'desktop/content/account/messages/inbox.html'},
    #    name='messages_inbox'),
    url(r'^inbox/$', account_messages_inbox, name='messages_inbox'),
    url(r'^sent/$', account_messages_sent, name='account_messages_sent'),
    url(r'^create/$', 'message_create',
        {'template_name': 'desktop/content/account/messages/create.html', 'form_class': NewMessageFormMultipleFriends, 'multiple': True},
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

ajax_urls = patterns('',
    url(r'^status-update/$', ajax_status_update, name='ajax_status_update'),
    url(r'^account-links/$', ajax_account_links, name='ajax_account_links'),
    url(r'^sign-out/$', ajax_sign_out, name='ajax_sign_out'),
    url(r'^home/friends/$', ajax_home_friends, name='ajax_home_friends'),
    url(r'^home/status-updates/$', ajax_home_status_updates, name='ajax_home_status_updates'),
    url(r'^like-stamp/(?P<slug>[\w-]+)/$', ajax_likes_stamp, name='ajax_likes_stamp'),
)

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    
    url(r'^facebook/', include('broadcastcms.facebook_integration.urls')),
    
    url(r'comment-add/$', comment_add, name='comment_add'),
    
    url(r'^admin/(.*)', admin.site.root),
    
    url(r'^ajax/', include(ajax_urls)),
    
    url(r'^account/settings/image/$', account_settings_image, name='account_settings_image'),
    url(r'^account/settings/details/$', account_settings_details, name='account_settings_details'),
    url(r'^account/settings/subscriptions/$', account_settings_subscriptions, name='account_settings_subscriptions'),
    url(r'^account/friends/my/$', account_friends_my, name='account_friends_my'),
    url(r'^account/friends/activity/$', account_friends_activity, name='account_friends_activity'),
    url(r'^account/friends/find/$', account_friends_find, name='account_friends_find'),
    url(r'^account/friends/add/(?P<user_pk>[\w-]+)/$$', account_friends_add, name='account_friends_add'),
    url(r'^account/friends/remove/(?P<user_pk>[\w-]+)/$$', account_friends_remove, name='account_friends_remove'),
    url(r'^account/friends/response/(\d+)/$',
        'friends.views.respond_to_friendship_invitation',
        {'redirect_to_view': 'account_friends_my'},
        name='account_friends_reply'),
    url(r'^account/friends/facebook/$',
        'broadcastcms.facebook_integration.views.invite',
        name='account_friends_facebook_invite'),
    url(r'^account/friends/facebook/add/$',
        'broadcastcms.facebook_integration.views.add_facebook_friends',
        name='account_friends_facebook_add'),
    url(r'^account/history/$', account_history, name='account_history'),
    url(r'^account/messages/', include(messages_urls)),
    url(r'^account/status/', include('broadcastcms.status.urls')),
    
    url(r'^account/login/', account_login, name='account_login'),
    
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

    url(r'reviews/(?P<slug>[\w-]+)/$', reviews_content, name='reviews_content'),
    url(r'reviews/$', reviews, name='reviews'),
    
    url(r'shows/line-up/$', ShowsLineUp(), name='shows_line_up'),
    url(r'shows/(?P<slug>[\w-]+)/$', shows_dj_blog, name='shows_dj_blog'),
    url(r'shows/(?P<slug>[\w-]+)/profile/$', shows_dj_profile, name='shows_dj_profile'),
    url(r'shows/(?P<slug>[\w-]+)/contact/$', shows_dj_contact, name='shows_dj_contact'),
    url(r'shows/(?P<slug>[\w-]+)/appearances/$', shows_dj_appearances, name='shows_dj_appearances'),
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
