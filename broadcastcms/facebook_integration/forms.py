from django import forms
from django.contrib.auth.models import User, UserManager
from django.contrib.sites.models import Site

from broadcastcms.facebook_integration.models import FacebookFriendInvite
from broadcastcms.lite.models import UserProfile
from broadcastcms.fields import formfields


class FacebookRegistrationForm(forms.Form):
    username = formfields.UsernameField(
        max_length=100,
        label='Username:',
        help_text='Must be at least 4 characters, letters, numbers and underscores only.',
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={
            'required': 'Please enter a username.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
            'existing': 'Sorry, that username already exists.',
        }
    )
    email_address = forms.EmailField(
        max_length=100,
        label='Email:',
        help_text='We will send you account notices here - so make sure its good.',
        widget=forms.TextInput(attrs={'class':'required email'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    email_subscribe = forms.BooleanField(
        required=False,
        label='Email Subscribe',
        help_text='Send Me Email Alerts',
    )
    sms_subscribe = forms.BooleanField(
        required=False,
        label='SMS Subscribe',
        help_text='Send Me SMS Alerts',
    )
    accept_terms = forms.BooleanField(
        label='Legal Stuff:',
        help_text='I agree to the website terms of use',
        widget=forms.CheckboxInput(attrs={'class':'required'}),
        error_messages={'required': 'Please accept our terms &amp; conditions to continue.'}
    )
    use_facebook_picture = forms.BooleanField(
        required = False,
        label='Facebook Options:',
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
            email = self.cleaned_data["email_address"],
        )
        if self.user_info["first_name"]: 
            user.first_name = self.user_info["first_name"]
        if self.user_info["last_name"]:
            user.last_name = self.user_info["last_name"]
        user.save()
        
        FacebookFriendInvite.objects.create_friendships(user,
            self.user_info["uid"])
        
        # Create profile
        profile = user.profile
        profile.facebook_url = self.user_info["profile_url"]
        profile.facebook_id = self.user_info["uid"]
        profile.email_subscribe = self.cleaned_data["email_subscribe"]
        profile.sms_subscribe = self.cleaned_data["sms_subscribe"]
        profile.use_facebook_picture = self.cleaned_data["use_facebook_picture"]
        profile.save()
        
        return username, password


class FacebookPermissionsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("publish_facebook_comments", "publish_facebook_status",
            "publish_facebook_likes", "use_facebook_picture")
