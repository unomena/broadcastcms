from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from django.contrib import auth

from broadcastcms.facebook_integration.decorators import facebook_required
from broadcastcms.facebook_integration.forms import FacebookRegistrationForm


def finish_signup(request):
    template_name = "desktop/facebook_integration/finish_signup.html"
    
    user_info = request.session.get("fb_signup_info")
    if not user_info:
        return HttpResponse("no signup data available, not good")
    
    if request.method == "POST":
        form = FacebookRegistrationForm(request.POST, user_info=user_info)
        if form.is_valid():
            username, password = form.save()
            
            user = auth.authenticate(
                username=username, 
                password=password
            )
            if user:
                auth.login(request, user)
            
            del request.session["fb_signup_info"]
            
            return HttpResponseRedirect(reverse("home"))
    else:
        form = FacebookRegistrationForm()
    
    return direct_to_template(request, template_name, {
        "form": form,
        "first_name": user_info["first_name"],
    })


@facebook_required
def invite(request):
    return direct_to_template(request, 
        "desktop/facebook_integration/invite.html", {
        })
