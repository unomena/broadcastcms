from datetime import datetime

from django import forms
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, mail_managers

from broadcastcms.competition.models import CompetitionEntry
from broadcastcms.event.models import Province
from broadcastcms.fields import formfields
from broadcastcms.integration.captchas import ReCaptcha

from models import Settings


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label='Username',
        widget=forms.TextInput(attrs={'class':'required'}),
        error_messages={'required': 'Please enter a username.'}
    )
    password = forms.CharField(
        max_length=100, 
        label='Password',
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
        max_length=100,
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
        help_text='I agree to the website terms of use',
        widget=forms.CheckboxInput(attrs={'class':'required'}),
        error_messages={'required': 'Please accept our terms &amp; conditions</a> to complete registration.'}
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
        max_length=100,
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
        from_address = "%s <%s>" % (name, email)
        
        mail = EmailMessage(subject, message, from_address, recipients, headers={'From': from_address, 'Reply-To': from_address})
        mail.send(fail_silently=False)

def make_contact_form(request):
    user = request.user
    if request.user.is_authenticated():
        class AuthenticatedContactForm(_BaseContactForm):
            from_name = '%s %s' % (user.first_name, user.last_name)
            from_email = user.email

        return AuthenticatedContactForm
    else:
        class AnonymousContactForm(_BaseContactForm):
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
                label='',
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
