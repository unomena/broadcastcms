from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from friends.models import Friendship

from broadcastcms.history.models import HistoryEvent


@login_required
def my_history(request):
    events = HistoryEvent.objects.filter(user=request.user)
    return render_to_response("desktop/content/account/history/my_history.html", {
        "events": events,
    }, context_instance=RequestContext(request))


@login_required
def friends_history(request):
    friends = Friendship.objects.friends_for_user(request.user)
    friends = [o["friend"] for o in friends]
    events = HistoryEvent.objects.filter(user__in=friends)
    return render_to_response("desktop/content/account/history/friends_history.html", {
        "events": events,
    }, context_instance=RequestContext(request))
