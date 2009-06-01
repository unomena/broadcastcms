from django.db import models
from django import forms

class CommaSeperatedCharField(models.TextField):
    """
    Usefull for multiple choice string selection fields.
    """
    __metaclass__ = models.SubfieldBase
   
    def get_db_prep_value(self, value):
        return '|'.join(value)

    def to_python(self, value):
        if not isinstance(value, list):
            value = value.split('|')
        return value

    def formfield(self, **kwargs):
        #TODO: Deal with the case where we have no choices, widget renders improperly

        #Django coerces fields with choices to TypedChoiceFields, see django/db/models/fields/__init__.py line 318.
        #We obviously don't want that here, so we bypass coercion by disabling choices before super and 
        #enabling it again after super. We still have to pass choices to the form field through defaults though.

        
        #disable but save choices
        try:
            choices = self.get_choices(include_blank=False)
        except AttributeError:
            choices = [()]
        self._choices = choices
        
        #setup defaults
        defaults = {'form_class': forms.MultipleChoiceField,
                    'widget': forms.SelectMultiple,
                    'choices': choices}
        defaults.update(kwargs)

        #run super and enable choices
        field = super(CommaSeperatedCharField, self).formfield(**defaults)
        self._choices = choices
        return field
