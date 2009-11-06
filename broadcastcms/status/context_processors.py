from broadcastcms.status.models import StatusUpdate


def current_status(request):
    if request.user.is_authenticated():
        status = StatusUpdate.objects.current_status(request.user)
    else:
        status = None
    return {"current_status": status}
