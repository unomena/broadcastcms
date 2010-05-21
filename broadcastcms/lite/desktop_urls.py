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
    url(r'^create/$', 'message_create',
        {'template_name': 'desktop/content/account/messages/create.html', 'form_class': NewMessageFormMultipleFriends, 'multiple': True},
        name='message_create'),
    url(r'^create/(?P<user_id>\d+)/$', 'message_create',
        {'template_name': 'desktop/content/account/messages/create.html', 'multiple': True},
        name='message_create'),
    url(r'^thread/(?P<thread_id>\d+)/delete/$', 'thread_delete',
        name='messages_thread_delete'),
)

ajax_urls = patterns('',
    url(r'^sign-out/$', ajax_sign_out, name='ajax_sign_out'),
    url(r'^like-stamp/(?P<slug>[\w-]+)/$', ajax_likes_stamp, name='ajax_likes_stamp'),
    url(r'^poll-vote/(?P<slug>[\w-]+)/$', ajax_poll_vote, name='ajax_poll_vote'),
)

ssi_urls = patterns('',
    url(r'^account-links-node/$', ssi_account_links_node, name='ssi_account_links_node'),
    url(r'^status-update-node/$', ssi_status_update_node, name='ssi_status_update_node'),
    url(r'^comments-node/(?P<slug>[\w-]+)/$', ssi_comments_node, name='ssi_comments_node'),
    url(r'^(?P<slug>[\w-]+)/$', ssi_widget, name='ssi_widget'),
    url(r'^(?P<slug>[\w-]+)/(?P<section>[\w-]+)/$', ssi_widget, name='ssi_account_menu_widget'),
    #url(r'^your-friends/$', session_your_friends, name='session_your_friends'),
    #url(r'^status-updates/$', session_status_updates, name='session_status_updates'),
)

from facebookconnect.views import facebook_login,facebook_logout,setup
urlpatterns = patterns('',
    url(r'^$', layout_view, name='home'),
    
    url(r'^facebook/setup/$', layout_view, name="facebook_setup"),
    url(r'^facebook/login-redirect/$', facebook_login_redirect, name="facebook_login_redirect"),
    (r'^facebook/', include('facebookconnect.urls')),
    
    url(r'comment-add/$', comment_add, name='comment_add'),
    (r'^comments/', include('django.contrib.comments.urls')),
    
    url(r'^admin/(.*)', admin.site.root),
    
    (r'^ckeditor/', include('ckeditor.urls')),    
    
    url(r'^ajax/', include(ajax_urls)),
    
    url(r'^ssi/', include(ssi_urls)),
    
    url(r'^account/settings/image/$', account_settings_image, name='account_settings_image'),
    url(r'^account/settings/details/$', account_settings_details, name='account_settings_details'),
    url(r'^account/settings/subscriptions/$', account_settings_subscriptions, name='account_settings_subscriptions'),
    url(r'^account/friends/my/$', layout_view, name='account_friends_my'),
    url(r'^account/friends/activity/all/$', layout_view, name='account_friends_activity_all'),
    url(r'^account/friends/activity/(?P<user_pk>[\w-]+)/$', layout_view, name='account_friends_activity'),
    
    url(r'^account/friends/find/$', layout_view, name='account_friends_find'),
    url(r'^account/friends/add/(?P<user_pk>[\w-]+)/$$', account_friends_add, name='account_friends_add'),
    url(r'^account/friends/remove/(?P<user_pk>[\w-]+)/$$', account_friends_remove, name='account_friends_remove'),
    url(r'^account/friends/response/(\d+)/$',
        'friends.views.respond_to_friendship_invitation',
        {'redirect_to_view': 'account_friends_my'},
        name='account_friends_reply'),
    url(r'^account/friends/find/facebook/$', layout_view, name='account_friends_facebook_invite'),
    url(r'^account/friends/facebook/add/$',
        'broadcastcms.facebook_integration.views.add_facebook_friends',
        name='account_friends_facebook_add'),
    url(r'^account/history/$', layout_view, name='account_history'),

    url(r'^account/messages/inbox/$', layout_view, name='messages_inbox'),
    url(r'^account/messages/sent/$', layout_view, name='messages_sent'),
    url(r'^account/messages/create/$', layout_view, name='message_create'),
    url(r'^account/messages/thread/(?P<thread_id>\d+)/$', layout_view, name='messages_thread_detail'),
    url(r'^account/messages/', include(messages_urls)),
    
    url(r'account/password-reset-done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'desktop/modals/password_reset.html'}, name='password_reset_done'),
    url(r'account/password-reset-confirm/(?P<uidb36>[\w-]+)/(?P<token>[\w-]+)$', layout_view, name='password_reset_confirm'),
    url(r'account/password-reset-complete/$', layout_view, name='password_reset_complete'),
    
    url(r'^account/status/', include('broadcastcms.status.urls')),
    
    url(r'^account/login/', account_login, name='account_login'),
    
    url(r'chart/$', ChartView(), name='chart'),
    
    url(r'competitions/$', competitions, name='competitions'),
    url(r'competitions/rules/$', competitions_rules, name='competitions_rules'),
    url(r'competitions/(?P<slug>[\w-]+)/$', competitions_content, name='competitions_content'),
    
    url(r'^contact/$', contact, name='contact'),
    
    url(r'events/$', events, name='events'),
    url(r'events/(?P<slug>[\w-]+)/$', events_content, name='events_content'),
    
    url(r'multimedia/$', galleries, name='galleries'),
    url(r'multimedia/submit/$', multimedia_submit, name='multimedia_submit'),
    url(r'multimedia/submit-photos/$', multimedia_submit_photos, name='multimedia_submit_photos'),
    url(r'multimedia/submit-video/$', multimedia_submit_video, name='multimedia_submit_video'),
    url(r'multimedia/thanks/$', multimedia_submit_thanks, name='multimedia_submit_thanks'),
    url(r'multimedia/(?P<slug>[\w-]+)/$', galleries_content, name='galleries_content'),
    url(r'multimedia/video/(?P<slug>[\w-]+)/$', video_content, name='video_content'),
   
    url(r'info/(?P<section>[\w-]+)/$', info_content, name='info_content'),
    
    url(r'listen-live/$', listen_live, name='listen_live'),
    url(r'studio-cam/$', studio_cam, name='studio_cam'),
    
    url(r'^podcasts/rss/$', podcasts_rss, name='podcasts_rss'),
    url(r'^news/rss/$', news_rss, name='news_rss'),
    url(r'^news/(?P<filter_label>[\w-]+)/rss/$', news_rss_by_label, name='news_rss_by_label'),
    url(r'^chart/rss/$', chart_rss, name='chart_rss'),

    url(r'news/$', news, name='news'),
    url(r'news/(?P<slug>[\w-]+)/$', news_content, name='news_content'),

    url(r'modals/content/(?P<slug>[\w-]+)/$', modals_content, name='modals_content'),
    url(r'modals/login/$', modals_login, name='modals_login'),
    url(r'modals/password-reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'desktop/modals/password_reset.html'}, name='modals_password_reset'),
    url(r'modals/register/$', modals_register, name='modals_register'),

    url(r'reviews/(?P<slug>[\w-]+)/$', reviews_content, name='reviews_content'),
    url(r'reviews/$', layout_view, name='reviews'),
    
    url(r'shows/line-up/$', layout_view, name='shows_line_up'),
    url(r'shows/(?P<slug>[\w-]+)/blog/$', shows_dj_blog, name='shows_dj_blog'),
    url(r'shows/(?P<slug>[\w-]+)/podcasts/$', shows_dj_podcasts, name='shows_dj_podcasts'),
    url(r'shows/(?P<slug>[\w-]+)/podcasts/rss/$', shows_dj_podcasts_rss, name='shows_dj_podcasts_rss'),
    url(r'shows/(?P<castmember_slug>[\w-]+)/podcasts/(?P<podcast_slug>[\w-]+)/$', shows_dj_podcasts_content, name='shows_dj_podcasts_content'),
    url(r'shows/(?P<slug>[\w-]+)/profile/$', shows_dj_profile, name='shows_dj_profile'),
    url(r'shows/(?P<slug>[\w-]+)/contact/$', shows_dj_contact, name='shows_dj_contact'),
    url(r'shows/(?P<slug>[\w-]+)/appearances/$', shows_dj_appearances, name='shows_dj_appearances'),
    url(r'shows/(?P<castmember_slug>[\w-]+)/blog/(?P<content_slug>[\w-]+)/$', shows_dj_content, name='shows_dj_content'),
    url(r'shows/(?P<castmember_slug>[\w-]+)/appearances/(?P<content_slug>[\w-]+)/$', shows_dj_appearances_content, name='shows_dj_appearances_content'),

    url(r'search-results/$', search_results, name='search_results'),
    
    url(r'subscribe-newsletter/$', newsletter_subscribe, name='newsletter_subscribe'),
    
    url(r'validate/captcha/$',  validate_captcha,   name='validate_captcha'),
    url(r'validate/password/$', validate_password,  name='validate_password'),
    url(r'validate/password-confirm/$', validate_password_confirm,  name='validate_password_confirm'),
    url(r'validate/password-reset/$', validate_password_reset,  name='validate_password_reset'),
    url(r'validate/username/$', validate_username,  name='validate_username'),

    url(r'voting/(?P<slug>[\w-]+)/$', xmlhttprequest_vote_on_object, {'model': ContentBase, 'slug_field': 'slug', 'direction': 'up'}, name='xmlhttprequest_vote_on_object'),
    
    url(r'voting/status/(?P<object_id>[\w-]+)/$', xmlhttprequest_vote_on_object, {'model': StatusUpdate, 'direction': 'up'}, name='xmlhttprequest_vote_on_status'),

    url(r'(?P<pk>[\w-]+)/$', short_redirect,  name='short_redirect'),
)

if settings.SERVE_STATIC:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
