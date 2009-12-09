from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils import simplejson as json
from django.utils.text import truncate_words

from broadcastcms.status.models import StatusUpdate


@login_required
def update(request):
    if request.method == "POST":
        text = request.POST["text"][:160]
        StatusUpdate.objects.create(user=request.user, text=text,
            source=StatusUpdate.SITE_SOURCE)
        if request.is_ajax():
            return HttpResponse(json.dumps({"updated": True, "text": truncate_words(text, 6)}),
                mimetype="application/json")
        else:
            return redirect(update)
    return render_to_response("desktop/content/account/update_status.html", {
    }, context_instance=RequestContext(request))
