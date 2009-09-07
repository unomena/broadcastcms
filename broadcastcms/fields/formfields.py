import re

from django import forms
from django.contrib.auth.models import User
from django.forms.util import ValidationError


class UsernameField(forms.CharField):

    def clean(self, value):
        """
        Lowers value.
        Checks that value is at least 4 characters long.
        Checks that the value does not include non-alphanumeric characters, excluding "_".
        Checks that a username of the given value does not already exist.
        """
        value = value.lower()
        if len(value) < 4:
            raise ValidationError(self.error_messages['invalid_length'])
        
        if re.search(r'\W', value):
            raise ValidationError(self.error_messages['invalid_characters'])

        if User.objects.filter(username__exact=value):
            raise ValidationError(self.error_messages['existing'])
        
        return super(UsernameField, self).clean(value)
