from django import forms

from django.contrib.auth.models import User, UserManager


class FacebookRegistrationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    email_subscribe = forms.BooleanField(
        required = False,
        help_text = u"Yes, %s may send me updates via email."
    )
    
    def __init__(self, *args, **kwargs):
        self.user_info = kwargs.pop("user_info", None)
        super(FacebookRegistrationForm, self).__init__(*args, **kwargs)
    
    def save(self):
        username = self.cleaned_data["username"]
        password = UserManager().make_random_password(length=8)
        
        user = User.objects.create_user(
            username = username,
            password = password,
            email = self.cleaned_data["email"],
        )
        user.first_name = self.user_info["first_name"]
        user.last_name = self.user_info["last_name"]
        user.save()
        
        # Create profile
        profile = user.profile
        profile.facebook_url = self.user_info["profile_url"]
        profile.email_subscribe = self.cleaned_data["email_subscribe"]
        profile.save()
        
        return username, password