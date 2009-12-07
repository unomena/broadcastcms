from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from broadcastcms.facebook_integration.decorators import facebook_required
from broadcastcms.facebook_integration.forms import (FacebookRegistrationForm,
    FacebookPermissionsForm)
from broadcastcms.facebook_integration.models import FacebookFriendInvite
from broadcastcms.facebook_integration.utils import facebook_api_request, API_KEY

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


@login_required
@facebook_required
def invite(request):
    if request.method == "POST":
        fb_ids = request.POST.getlist("ids")
        for fb_id in fb_ids:
            FacebookFriendInvite.objects.create(user=request.user,
                fb_user_id=fb_id)
        return HttpResponseRedirect(reverse(invite))
    return direct_to_template(request, 
        "desktop/facebook_integration/invite.html", {
        })


@login_required
@facebook_required
def add_facebook_friends(request):
    uid = request.COOKIES[API_KEY + "_session_key"]
    fb_friends = facebook_api_request("friends.get", session_key=uid)
    users = User.objects.filter(userprofile__facebook_id__in=fb_friends)
    return direct_to_template(request,
        "desktop/facebook_integration/add_facebook_friends.html", {
            "users": users,
        }
    )

@login_required
@facebook_required
def permissions(request):
    if request.method == "POST":
        form = FacebookPermissionsForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect(request.get_full_path())
    else:
        form = FacebookPermissionsForm(instance=request.user.profile)
    return direct_to_template(request,"desktop/facebook_integration/permissions.html", {
        "form": form,
    })

def existing_user(request):
    """
    Checks wether a user exists for the given facebook info
    Used to check for page reload requirement on facebook modal login.
    """
    from broadcastcms.lite.models import UserProfile
    response = "false"
    params = {
        "uids": request.COOKIES[API_KEY + "_user"],
        "fields": "profile_url,first_name,last_name",
    }
    result = facebook_api_request("users.getInfo", **params)
    user_info = result[0]
    try:
        queryset = UserProfile.objects.select_related("user").filter(facebook_id = user_info["uid"])
        profile = queryset.get()
        response = "true"
    except UserProfile.DoesNotExist:
        respone = "false"
        
    return HttpResponse(response)
