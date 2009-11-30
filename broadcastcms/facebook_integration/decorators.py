from django.shortcuts import redirect


def facebook_required(function):
    def inner(request, *args, **kwargs):
        if not request.fb_authenticated:
            # TODO: We should redirect to a login page.
            return redirect("home")
        return function(request, *args, **kwargs)
    return inner
