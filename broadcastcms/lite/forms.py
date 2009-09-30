from datetime import datetime

from django import forms

from broadcastcms.competition.models import CompetitionEntry
from broadcastcms.event.models import Province
from broadcastcms.fields import formfields

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
            password_confirm = self.fields['password_confirm'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password_confirm'))
            password = self.fields['password'].widget.value_from_datadict(self.data, self.files, self.add_prefix('password'))
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
