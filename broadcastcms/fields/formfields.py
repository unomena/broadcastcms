import re

from django import forms
from django.forms.util import ValidationError


class UsernameField(forms.CharField):

    def clean(self, value):
        """
        Lowers value.
        Checks that the value does not include non-alphanumeric characters, excluding "_"
        """
        value = value.lower()
        if re.search(r'\W', value):
            raise ValidationError(self.error_messages['invalid'])

        return super(UsernameField, self).clean(value)
