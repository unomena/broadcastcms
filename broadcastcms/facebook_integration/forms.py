from django import forms
from django.contrib.auth.models import User, UserManager
from django.contrib.sites.models import Site

from broadcastcms.facebook_integration.models import FacebookFriendInvite
from broadcastcms.lite.models import UserProfile


class FacebookRegistrationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    email_subscribe = forms.BooleanField(
        required = False,
        help_text = u"Yes, %(site_name)s may send me updates via email."
    )
    use_facebook_picture = forms.BooleanField(
        required = False,
        help_text = "I want to use my Facebook picture on this site."
    )
    
    def __init__(self, *args, **kwargs):
        self.user_info = kwargs.pop("user_info", None)
        super(FacebookRegistrationForm, self).__init__(*args, **kwargs)
        
        site = Site.objects.get_current()
        
        self.fields["email_subscribe"].help_text = self.fields["email_subscribe"].help_text % {"site_name": site.name}
    
    def save(self):
        username = self.cleaned_data["username"]
        password = UserManager().make_random_password(length=8)
        
        user = User.objects.create_user(
            username = username,
            password = password,
            email = self.cleaned_data["email"],
        )
        user.first_name = self.user_info["first_name"] if self.user_info["first_name"] else ' '
        user.last_name = self.user_info["last_name"] if self.user_info["last_name"] else ' '
        user.save()
        
        FacebookFriendInvite.objects.create_friendships(user,
            self.user_info["uid"])
        
        # Create profile
        profile = user.profile
        profile.facebook_url = self.user_info["profile_url"]
        profile.facebook_id = self.user_info["uid"]
        profile.email_subscribe = self.cleaned_data["email_subscribe"]
        profile.use_facebook_picture = self.cleaned_data["use_facebook_picture"]
        profile.save()
        
        return username, password


class FacebookPermissionsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("publish_facebook_comments", "publish_facebook_status",
            "publish_facebook_likes", "use_facebook_picture")
