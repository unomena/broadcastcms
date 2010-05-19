from datetime import datetime
import threading
import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.forms import CommentForm
from django.core.mail import EmailMessage, mail_managers
from django.utils.safestring import mark_safe

from friends.models import Friendship
from user_messages.forms import NewMessageFormMultiple
from facebookconnect.forms import FacebookUserCreationForm

from broadcastcms.competition.models import CompetitionEntry
from broadcastcms.event.models import Province
from broadcastcms.fields import formfields
from broadcastcms.integration.captchas import ReCaptcha
from broadcastcms.gallery.models import Gallery, GalleryImage
from broadcastcms.video.models import Video
from broadcastcms.video import thumbnails

from models import Settings

class FacebookRegistrationForm(FacebookUserCreationForm):
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
    email = forms.EmailField(
        max_length=100,
        label='Email:',
        help_text='We will send you account notices here - so make sure its good.',
        widget=forms.TextInput(attrs={'class':'required email'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    email_subscribe = forms.BooleanField(
        required=False,
        label='Email Subscribe',
        help_text='Send Me Email Alerts.',
    )
    sms_subscribe = forms.BooleanField(
        required=False,
        label='SMS Subscribe',
        help_text='Send Me SMS Alerts.',
    )
    accept_terms = forms.BooleanField(
        label='Legal Stuff:',
        help_text='I agree to the website terms of use.',
        widget=forms.CheckboxInput(attrs={'class':'required'}),
        error_messages={'required': 'Please accept our terms &amp; conditions to continue.'}
    )
    use_facebook_picture = forms.BooleanField(
        required = False,
        label='Facebook Options:',
        help_text = "I want to use my Facebook picture on this site."
    )
    
    def save(self):
        user = super(FacebookRegistrationForm, self).save()

        # Create profile
        profile = user.profile
        profile.email_subscribe = self.cleaned_data["email_subscribe"]
        profile.sms_subscribe = self.cleaned_data["sms_subscribe"]
        profile.use_facebook_picture = self.cleaned_data["use_facebook_picture"]
        profile.save()
        
        return user

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='Username: ',
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter a username.'}
    )
    password = forms.CharField(
        max_length=100, 
        label='Password: ',
        widget=forms.PasswordInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter a password.'}
    )
    
class MobileLoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='Username:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter a username.'}
    )
    password = forms.CharField(
        max_length=30, 
        label='Password:',
        widget=forms.PasswordInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter a password.'}
    )
    
class RegistrationForm(forms.Form):
    username = formfields.UsernameField(
        max_length=30,
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
    first_name = forms.CharField(
        max_length=100,
        label='Name:',
        help_text="First Name and Last.",
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter your name.'}
    )
    last_name = forms.CharField(
        max_length=100,
        label='Surname:',
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter your surname.'}
    )
    email_address = forms.EmailField(
        max_length=100,
        label='Email:',
        help_text='We will send you account notices here - so make sure its good.',
        widget=forms.TextInput(attrs={'class':'required email'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    recaptcha_response_field = forms.CharField(
        max_length=100,
        label='Human?',
        help_text='Spam prevention code. Enter the words above.',
        widget=forms.TextInput(attrs={'class':'required', 'id': 'recaptcha_response_field', 'autocomplete': 'off'}),
        error_messages={'required': 'Please enter the words above.'}
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
        help_text=mark_safe('I agree to the website <a class="mb_link" href="/info/terms">terms of use.</a>'),
        widget=forms.CheckboxInput(attrs={'class':'required'}),
        error_messages={'required': 'Please accept our terms &amp; conditions to continue.'}
    )
    
class MobileRegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        label='Name:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your name.'}
    )
    last_name = forms.CharField(
        max_length=30,
        label='Surname:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your surname.'}
    )
    mobile_number = forms.CharField(
        max_length=20,
        label='Mobile (Int. Format: +2782 123 4567):',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your mobile number.'}
    )
    email_address = forms.EmailField(
        max_length=75,
        label='Email:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    username = formfields.UsernameField(
        max_length=30,
        label='Alias:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={
            'required': 'Please enter a username.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
            'existing': 'Sorry, that username already exists.',
        }
    )
    password = formfields.PasswordField(
        max_length=30,
        label='Password:',
        initial = '',
        widget=forms.PasswordInput(attrs={'class':'text'}),
        error_messages={
            'required': 'Please enter a username.',
            'invalid_length': 'Please enter at least 8 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
        }
    )
    password_confirm = formfields.PasswordField(
        label='Confirm Password:',
        initial = '',
        widget=forms.PasswordInput(attrs={'class':'text'}),
        error_messages={
            'required': 'Please confirm your new password.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
        },
        required=False,
    )
    email_subscribe = forms.BooleanField(
        required=False,
        label='',
        help_text='Send Me Email Alerts',
    )
    sms_subscribe = forms.BooleanField(
        required=False,
        label='',
        help_text='Send Me SMS Alerts',
    )
    accept_terms = forms.BooleanField(
        label='',
        help_text='I agree to the website <a href="/terms/">terms of use</a>',
        error_messages={'required': 'Please accept our terms &amp; conditions to complete registration.'}
    )
    def is_valid(self):
        # Base validate
        valid = super(MobileRegistrationForm, self).is_valid()

        # Validate image size
        if not self._errors.has_key('password_confirm'):
            try:
                password_confirm = self.fields['password_confirm'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password_confirm'))
            except KeyError:
                password_confirm = None
            try:
                password = self.fields['password'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password'))
            except KeyError:
                password = None
            if password and password_confirm:
                if password != password_confirm:
                    self._errors['password_confirm'] = ['Passwords do not match.',]
                    valid = False

        return valid

class ProfileForm(forms.Form):
    username = formfields.UsernameField(
        max_length=30,
        label='Alias:',
        help_text='Must be at least 4 characters, letters, numbers and underscores only.',
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={
            'required': 'Please enter a username.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
            'existing': 'Sorry, that username already exists.',
        }
    )
    first_name = forms.CharField(
        max_length=100,
        label='Name:',
        help_text="First Name and Last.",
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter your name.'}
    )
    last_name = forms.CharField(
        max_length=100,
        label='Surname:',
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter your surname.'}
    )
    email_address = forms.EmailField(
        max_length=100,
        label='Email:',
        help_text='We will send you account notices here - so make sure its good.',
        widget=forms.TextInput(attrs={'class':'required email'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    mobile_number = forms.CharField(
        max_length=100,
        label='Mobile Number:',
        help_text="International Format: +2782 123 4567",
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter your mobile number.'}
    )
    password = formfields.PasswordField(
        max_length=100, 
        label='Password:',
        help_text="Must be at least 4 characters, letters, numbers and underscores only.",
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Please enter a new password.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
        },
        required=False,
    )
    password_confirm = formfields.PasswordField(
        max_length=100, 
        label='Confirm Password:',
        help_text="Make sure it's the same as the above.",
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Please confirm your new password.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
        },
        required=False,
    )
    city = forms.CharField(
        max_length=100,
        label='City/Town:',
        error_messages={'required': 'Please enter your city/town.'},
        required=False,
    )
    province = forms.ModelChoiceField(
        label='Province:',
        help_text="Please select your province.",
        queryset=Province.permitted.all().order_by('name'),
        widget=forms.Select(attrs={'class':'province'}),
        required=False,
    )
    birth_date_day = forms.ChoiceField(
        required=False,
        choices=[('', 'Day'),] + [(i, i) for i in range(1,32)],
        widget=forms.Select(attrs={'class':'day'}),
    )
    birth_date_month = forms.ChoiceField(
        required=False,
        choices=[('', 'Month'),] + [(i, i) for i in range(1,13)],
        widget=forms.Select(attrs={'class':'month'}),
    )
    birth_date_year = forms.ChoiceField(
        required=False,
        choices=[('', 'Year'),] + [(i, i) for i in range(1920, datetime.now().year + 1)],
        widget=forms.Select(attrs={'class':'month'}),
    )

    def is_valid(self):
        # Base validate
        valid = super(ProfileForm, self).is_valid()

        # Validate image size
        if not self._errors.has_key('password_confirm'):
            try:
                password_confirm = self.fields['password_confirm'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password_confirm'))
            except KeyError:
                password_confirm = None
            try:
                password = self.fields['password'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password'))
            except KeyError:
                password = None
            if password and password_confirm:
                if password != password_confirm:
                    self._errors['password_confirm'] = ['Passwords do not match.',]
                    valid = False

        return valid
    
class MobileProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        label='Name:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your name.'}
    )
    last_name = forms.CharField(
        max_length=30,
        label='Surname:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your surname.'}
    )
    mobile_number = forms.CharField(
        max_length=20,
        label='Mobile (Int. Format: +2782 123 4567):',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your mobile number.'}
    )
    email_address = forms.EmailField(
        max_length=75,
        label='Email:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    username = formfields.UsernameField(
        max_length=30,
        label='Alias:',
        widget=forms.TextInput(attrs={'class':'text'}),
        error_messages={
            'required': 'Please enter a username.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
            'existing': 'Sorry, that username already exists.',
        }
    )
    password = formfields.PasswordField(
        max_length=30,
        label='Password:',
        widget=forms.PasswordInput(attrs={'class':'text'}),
        error_messages={
            'required': 'Please enter a username.',
            'invalid_length': 'Please enter at least 8 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
        }
    )
    password_confirm = formfields.PasswordField(
        label='Confirm Password:',
        widget=forms.PasswordInput(attrs={'class':'text'}),
        error_messages={
            'required': 'Please confirm your new password.',
            'invalid_length': 'Please enter at least 4 characters.',
            'invalid_characters': 'Only letters, numbers and underscores.',
        }
    )
    email_subscribe = forms.BooleanField(
        required=False,
        label='',
        help_text='Send Me Email Alerts',
    )
    sms_subscribe = forms.BooleanField(
        required=False,
        label='',
        help_text='Send Me SMS Alerts',
    )
    def is_valid(self):
        # Base validate
        valid = super(MobileProfileForm, self).is_valid()

        # Validate image size
        if not self._errors.has_key('password_confirm'):
            try:
                password_confirm = self.fields['password_confirm'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password_confirm'))
            except KeyError:
                password_confirm = None
            try:
                password = self.fields['password'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password'))
            except KeyError:
                password = None
            if password and password_confirm:
                if password != password_confirm:
                    self._errors['password_confirm'] = ['Passwords do not match.',]
                    valid = False

        return valid

class ProfilePictureForm(forms.Form):
    image = forms.ImageField(
        required=False,
        label="Profile Picture",
        help_text="GIF, JPG &amp; PNG image format are accepted. (Maximum 1MB.)<br />Square images will look best.",
        widget=forms.FileInput(attrs={'id':'avatar'})
    )
    
    def is_valid(self):
        # Base validate
        valid = super(ProfilePictureForm, self).is_valid()

        # Validate image size
        if not self._errors.has_key('image'):
            image = self.fields['image'].widget.value_from_datadict(self.data, self.files, self.add_prefix('image'))
            if image:
                if (image.size / 1048576.0) >= 1:
                    self._errors['image'] = ['The image you uploaded is too big.',]
                    valid = False
       
        return valid

class ProfileSubscriptionsForm(forms.Form):
    email_subscribe = forms.BooleanField(
        required=False,
        label='Email<br />Alerts:',
        help_text='Send Me Email Alerts',
    )
    sms_subscribe = forms.BooleanField(
        required=False,
        label='Mobile<br />Alerts:',
        help_text='Send Me SMS Alerts',
    )

class _BaseCompetitionForm(forms.Form):
    def create_entry(self, competition, user):
        answer = self.get_answer()
        CompetitionEntry(
            competition = competition,
            user = user,
            answer = answer,
        ).save()

def make_competition_form(competition):
    options = competition.options.permitted()
    label = "Your Answer: "

    if options:
        class _OptionsCompetitionForm(_BaseCompetitionForm):
            answer = forms.ModelChoiceField(
                label=label,
                queryset=options,
                empty_label=None,
                widget=forms.Select(attrs={'class':'compchoice'}),
            )
            def get_answer(self):
                return self.cleaned_data['answer'].title

        return _OptionsCompetitionForm
    else:
        class _AnswerCompetitionForm(_BaseCompetitionForm):
            answer = forms.CharField(
                max_length=255,
                label=label,
                required=True,
            )
            def get_answer(self):
                return self.cleaned_data['answer']

        return _AnswerCompetitionForm

class _BaseContactForm(forms.Form):
    subject = forms.CharField(
        max_length=512,
        label='Subject',
    )
    message = forms.CharField(
        max_length=10000,
        label='Message',
        widget=forms.Textarea(),
        error_messages={'required':'Please enter a message.'}
    )

    def is_valid(self, request=None):
        """
        Override purely to provide for the extra request parameter, used by AnonymousContactForm
        """
        return super(_BaseContactForm, self).is_valid()
        
    
    def get_recipients(self):
        current_site = Site.objects.get_current()
        site_name = current_site.name
        recipients = []
        
        settings = Settings.objects.all()
        if settings:
            contact_email_recipients = settings[0].contact_email_recipients
            if contact_email_recipients:
                split_recipients = [recipient.replace('\r', '') for recipient in contact_email_recipients.split('\n')]
                for recipient in split_recipients:
                    if recipient:
                        recipients.append(recipient)

        if not recipients:
            mail_managers('Error: No email address specified', 'Users are trying to contact %s for which no contact email recipients are specified.' % site_name, fail_silently=False)
        return recipients
    
    def send_message(self):
        current_site = Site.objects.get_current()
        site_name = current_site.name
        
        name = self.from_name
        email = self.from_email
        subject = "Contact message from %s: %s" % (site_name, self.cleaned_data['subject'])
        message = self.cleaned_data['message']
        recipients = self.get_recipients()
        if recipients:
            from_address = "%s <%s>" % (name, email)
        
            mail = EmailMessage(subject, message, from_address, recipients, headers={'From': from_address, 'Reply-To': from_address})
            t = threading.Thread(target=mail.send, kwargs={'fail_silently': False})
            t.setDaemon(True)
            t.start()

class _BaseCastmemberContactForm(_BaseContactForm):
    def __init__(self, castmember, *args, **kwargs):
        self.castmember = castmember
        super(_BaseCastmemberContactForm, self).__init__(*args, **kwargs)

    def get_recipients(self):
        castmember_email = self.castmember.owner.email
        if not castmember_email:
            mail_managers('Error: No email address specified', 'Users are trying to contact %s for which no email address could be found.' % self.castmember.title, fail_silently=False)
            recipients = None
        else:
            recipients = [castmember_email,]
        return recipients

class _BaseMobileContactForm(forms.Form):
    
    from_name = ''
    from_email = ''
    
    def get_recipients(self):
        current_site = Site.objects.get_current()
        site_name = current_site.name
        recipients = []
        
        settings = Settings.objects.all()
        if settings:
            contact_email_recipients = settings[0].contact_email_recipients
            if contact_email_recipients:
                split_recipients = [recipient.replace('\r', '') for recipient in contact_email_recipients.split('\n')]
                for recipient in split_recipients:
                    if recipient:
                        recipients.append(recipient)

        if not recipients:
            mail_managers('Error: No email address specified', 'Users are trying to contact %s for which no contact email recipients are specified.' % site_name, fail_silently=False)
        return recipients
    
    def send_message(self):
        current_site = Site.objects.get_current()
        site_name = current_site.name
        
        name = self.from_name
        email = self.from_email
        subject = "Contact message from %s: %s" % (site_name, self.cleaned_data['subject'])
        message = self.cleaned_data['message']
        recipients = self.get_recipients()
        from_address = "%s <%s>" % (name, email)
        
        mail = EmailMessage(subject, message, from_address, recipients, headers={'From': from_address, 'Reply-To': from_address})
        mail.send(fail_silently=False)

def make_contact_form(request, base_class=_BaseContactForm):
    user = request.user
    if request.user.is_authenticated():
        class AuthenticatedContactForm(base_class):
            from_name = '%s %s' % (user.first_name, user.last_name)
            from_email = user.email

        return AuthenticatedContactForm
    else:
        class AnonymousContactForm(base_class):
            name = forms.CharField(
                max_length=100,
                label='Your Name',
            )
            email = forms.EmailField(
                max_length=100,
                label='Your Email',
                error_messages={'required':'Please enter your email address.'}
            )
            recaptcha_response_field = forms.CharField(
                max_length=100,
                label='Human?',
                help_text='Spam prevention code. Enter the words above.',
                widget=forms.TextInput(attrs={'class':'required', 'id': 'recaptcha_response_field', 'autocomplete': 'off'}),
                error_messages={'required': 'Please enter the words above.'}
            )
            from_name = property(lambda f: f.cleaned_data['name'])
            from_email = property(lambda f: f.cleaned_data['email'])
        
            def is_valid(self, request):
                # Base validate
                valid = super(AnonymousContactForm, self).is_valid()

                # Validate Captcha
                if not self._errors.has_key('recaptcha_response_field'):
                    if not ReCaptcha().verify(request):
                        self._errors['recaptcha_response_field'] = ['Incorrect, please try again.',]
                        valid = False
                return valid

        return AnonymousContactForm
    
def make_mobile_contact_form(request):
    user = request.user
    if request.user.is_authenticated():
        class AuthenticatedMobileContactForm(_BaseMobileContactForm):
            subject = forms.CharField(
                max_length=150,
                widget=forms.HiddenInput(),
                required = False
            )
            message = forms.CharField(
                max_length=10000,
                label='Message',
                widget=forms.Textarea(),
                error_messages={'required':'Please enter a message.'}
            )

        return AuthenticatedMobileContactForm
    else:
        class AnonymousMobileContactForm(_BaseMobileContactForm):
            name = forms.CharField(
                max_length=100,
                label='Your Name',
                widget=forms.TextInput(attrs={'class':'text'}),
            )
            email = forms.EmailField(
                max_length=100,
                label='Your Email',
                widget=forms.TextInput(attrs={'class':'text'}),
                error_messages={'required':'Please enter your email address.'}
            )
            mobile_number = forms.CharField(
                max_length=20,
                label='Your Mobile (Int. Format: +2782 123 4567):',
                widget=forms.TextInput(attrs={'class':'text'}),
            )
            subject = forms.CharField(
                max_length=150,
                widget=forms.HiddenInput(),
                required = False
            )
            message = forms.CharField(
                max_length=10000,
                label='Message',
                widget=forms.Textarea(),
                error_messages={'required':'Please enter a message.'}
            )

        return AnonymousMobileContactForm

class NewMessageFormMultipleFriends(NewMessageFormMultiple):
    to_user = forms.ModelMultipleChoiceField(Friendship.objects)

    def __init__(self, *args, **kwargs):
        super(NewMessageFormMultipleFriends, self).__init__(*args, **kwargs)
    
        # give form fields nice labels
        self.fields['subject'].label = 'Subject'
        self.fields['to_user'].label = 'Recipient/s'
        self.fields['content'].label = 'Message'
        
        # set error messages
        self.fields['to_user'].error_messages['invalid_pk_value'] = u'"%s" is not a valid recipient. Please correct or remove and try again.'
        
        # limit user options to friends
        if self.initial.get('to_user') is None:
            friend_pks = [object['friend'].pk for object in self.fields['to_user'].queryset.friends_for_user(kwargs['user'])]
            qs = User.objects.filter(pk__in=friend_pks).order_by('username')
            self.fields['to_user'].queryset = qs



class SubmitPicturesForm(forms.Form):
    """
    Multimedia page pictures submission form.
    """
    
    title = forms.CharField(max_length=200)
    tell_us_more = forms.CharField(max_length=200, label="Tell us More", required=False)
    file1 = forms.ImageField()
    file2 = forms.ImageField(required=False)
    file3 = forms.ImageField(required=False)
    file4 = forms.ImageField(required=False)
    file5 = forms.ImageField(required=False)
    file6 = forms.ImageField(required=False)
    file7 = forms.ImageField(required=False)
    file8 = forms.ImageField(required=False)
    file9 = forms.ImageField(required=False)
    file10 = forms.ImageField(required=False)
    permission_check = forms.BooleanField(required=True)
    ghfm_use_check = forms.BooleanField(required=True)
    
    file_fields = []
    
    
    def __init__(self, *args, **kwargs):
        super(SubmitPicturesForm, self).__init__(*args, **kwargs)
        self.file_fields = []
        field_count = 1
        done = False
        # get all of the file fields
        while not done:
            try:
                self.file_fields.append(self.fields['file%d' % field_count])
                field_count += 1
            except:
                done = True
        
        
    def save(self, request):
        data = self.cleaned_data
        # create a gallery
        gallery = Gallery(title=data['title'], description=data['tell_us_more'],
            image=data['file1'], owner=request.user)
        gallery.save()
        
        # add the images to the gallery
        for i in range(1, len(self.file_fields)+1):
            cur_file = data['file%d' % i]
            if cur_file:
                img = GalleryImage(gallery=gallery, title=str(cur_file), description=str(cur_file), image=cur_file, owner=request.user)
                img.save()
                
        return True
    
    
    
    
class SubmitVideoForm(forms.Form):
    """
    Multimedia page video submission form.
    """
    
    title = forms.CharField(max_length=200)
    tell_us_more = forms.CharField(max_length=200, label="Tell us More")
    embed_code = forms.CharField(max_length=1024)
    permission_check = forms.BooleanField(required=True)


    # Regular expressions for parsing embed code
    # YouTube embeds
    youtube_full_regex = r'\s*<object\s+width="(?P<width1>\d+)"\s+height="(?P<height1>\d+)">\s*<param\s+name="movie"\s+value="(?P<url1>(?P<protocol1>(http|https))://(?P<subdomain1>[a-z]+)\.youtube\.(?P<domain1>[a-z]+)/v/(?P<videocode1>[a-zA-Z0-9]*)[a-zA-Z0-9&=_]*)">\s*</param>\s*<param\s+name="allowFullScreen"\s+value="true">\s*</param>\s*<param\s+name="allowscriptaccess"\s+value="always">\s*</param>\s*<embed\s+src="(?P<url2>(?P<protocol2>(http|https))://(?P<subdomain2>[a-z]+)\.youtube\.(?P<domain2>[a-z]+)/v/(?P<videocode2>[a-zA-Z0-9]*)[a-zA-Z0-9&=_]*)"\s+type="application/x-shockwave-flash"\s+allowscriptaccess="always"\s+allowfullscreen="true"\s+width="(?P<width2>\d+)"\s+height="(?P<height2>\d+)">\s*</embed>\s*</object>\s*'
    youtube_partial_regex = r'\s*(?P<protocol>(http|https))://(?P<subdomain>[a-zA-Z0-9\.]*)\.youtube\.(?P<domain>[a-z]+)/watch\?v=(?P<videolink>[a-zA-Z0-9&=_]*)\s*'
    # Zoopy embeds
    zoopy_full_regex = r'\s*<object\s+classid="clsid:(?P<clsid>[a-zA-Z0-9-]*)"\s+codebase="http://macromedia.com/cabs/swflash.cab#version=(?P<flashversion>[0-9,]*)"\s+id="zoopy-video-(?P<zoopyid1>\d+)"\s+width="(?P<width1>\d+)"\s+height="(?P<height1>\d+)">\s*<param\s+name="movie"\s+value="http://media.z2.zoopy.com/video-offsite.swf"\s*/>\s*<param\s+name="flashvars"\s+value="id=(?P<zoopyid2>\d+)"\s*/>\s*<param\s+name="quality"\s+value="high"\s*/>\s*<param\s+name="bgcolor"\s+value="#(?P<bgcolor1>\d+)"\s*/>\s*<param\s+name="allowscriptaccess"\s+value="always"\s*/>\s*<param\s+name="allowfullscreen"\s+value="true"\s*/>\s*<param\s+name="wmode"\s+value="opaque"\s*/>\s*<embed\s+src="http://media.z2.zoopy.com/video-offsite.swf"\s+allowfullscreen="true"\s+flashvars="id=(?P<zoopyid3>\d+)"\s+bgcolor="#(?P<bgcolor2>\d+)"\s+width="(?P<width2>\d+)"\s+height="(?P<height2>\d+)"\s+type="application/x-shockwave-flash"\s+allowscriptaccess="always"\s+wmode="opaque">\s*</embed>\s*</object>\s*'
    
    # can either be 'y' for YouTube or 'z' for Zoopy
    video_type = None
    # video details
    video_id = None
    # default video width and height
    video_width = 480
    video_height = 385



    def clean_embed_code(self):
        """
        Checks the embed code to see whether it's a YouTube or Zoopy video.
        
        TODO: check video dimensions and resize by aspect ratio if necessary.
        """
        
        code = self.cleaned_data['embed_code']
        
        # check which embed code it is
        youtube_full = re.compile(self.youtube_full_regex)
        m = youtube_full.match(code)
        if not m:
            youtube_partial = re.compile(self.youtube_partial_regex)
            m = youtube_partial.match(code)
            # if it's a partial YouTube link
            if m:
                # make it a full one
                code = '<object width="%(width)s" height="%(height)s"><param name="movie" value="%(protocol)s://%(subdomain)s.youtube.%(domain)s/v/%(videolink)s&hl=en_US&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="%(protocol)s://%(subdomain)s.youtube.%(domain)s/v/%(videolink)s&hl=en_US&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%(width)s" height="%(height)s"></embed></object>' % {
                        'width': self.video_width, 'height': self.video_height, 'videolink': m.group('videolink'), 'domain': m.group('domain'), 'subdomain': m.group('subdomain'), 'protocol': m.group('protocol'),
                    }
                self.video_id = m.group('videolink')
                self.video_type = 'y'
            else:
                # check if it's a Zoopy embed
                zoopy_full = re.compile(self.zoopy_full_regex)
                m = zoopy_full.match(code)
                if not m:
                    raise forms.ValidationError('Invalid embed code.')
                else:
                    self.video_type = 'z'
                    self.video_id = m.group('zoopyid1')
        else:
            self.video_type = 'y'
            self.video_id = m.group('videocode1')
            
        return code
    
    
    def save(self, request):
        data = self.cleaned_data
        # check which type of video it is
        if self.video_type == 'y':
            # get the thumbnail from YouTube
            thumbnail = thumbnails.get_youtube_thumbnail(self.video_id)
        else:
            # get the thumbnail from Zoopy
            thumbnail = thumbnails.get_zoopy_thumbnail(self.video_id)
        # create the video
        video = Video(code=data['embed_code'], title=data['title'], description=data['tell_us_more'], image=thumbnail, owner=request.user)
        video.save()
        return True
