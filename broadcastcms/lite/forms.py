from django import forms

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
