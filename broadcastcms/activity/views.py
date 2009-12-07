from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from friends.models import Friendship

from broadcastcms.activity.models import ActivityEvent


# XXX SS:I've moved this to lite/desktop_views.py under account_history
#@login_required
#def my_activity(request):
#    events = ActivityEvent.objects.filter(user=request.user)
#    return render_to_response("desktop/content/account/activity/my_activity.html", {
#        "events": events,
#    }, context_instance=RequestContext(request))


# XXX SS:I've moved this to lite/desktop_views.py under account_friends_activity
#@login_required
#def friends_activity(request):
#    friends = Friendship.objects.friends_for_user(request.user)
#    friends = [o["friend"] for o in friends]
#    events = ActivityEvent.objects.filter(user__in=friends)
#    return render_to_response("desktop/content/account/activity/friends_activity.html", {
#        "events": events,
#    }, context_instance=RequestContext(request))
