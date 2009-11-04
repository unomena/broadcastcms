def facebook_required(function):
    def inner(request, *args, **kwargs):
        if not request.fb_authenticated:
            # TODO: do a redirect or something sensible here
            raise ValueError("Need Facebook Auth for this")
        return function(request, *args, **kwargs)
    return inner
