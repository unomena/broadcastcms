from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from broadcastcms.history.models import HistoryEvent


@login_required
def my_history(request):
    events = HistoryEvent.objects.filter(user=request.user)
    return render_to_response("desktop/content/account/history/my_history.html", {
        "events": events,
    }, context_instance=RequestContext(request))
