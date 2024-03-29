from datetime import timedelta
from copy import deepcopy

from django import forms
from django.contrib import admin
from django.forms.formsets import DELETION_FIELD_NAME
from models import *
from broadcastcms.base.admin import ModelBaseAdmin, ModelBaseTabularInline

# TODO: I'm killing recurring entry inline functionality for now
# until it's refactored to be more user friendly and all its 
# associated bugs have been stomped (SS)  
"""
RECURRING_CHOICES = (
    ('n', '(None)'),
    ('d', 'Daily'),
    ('w', 'Weekly'),
    ('f', 'Fortnightly'),
)


class EntryInlineForm(forms.ModelForm):
    recurring = forms.ChoiceField(
        label='Recurring',
        required=False,
        choices=RECURRING_CHOICES,
    )
    recurring_count = forms.IntegerField(
        label='Times Recurring',
        required=False,
    )


class EntryInlineFormSet(forms.models.BaseInlineFormSet):
    def save_new_objects(self, commit=True):
        super(EntryInlineFormSet, self).save_new_objects(commit)
        for form in self.extra_forms:
            if not form.has_changed():
                continue
            if self.can_delete and form.cleaned_data[DELETION_FIELD_NAME]:
                continue
            recurring, count = form.cleaned_data['recurring'], form.cleaned_data['recurring_count']
            # create the required amount of recurrences
            if not recurring == '(None)':
                for i in range(0, count):
                    # alter the dates accoring to the form input
                    start, end = form.cleaned_data['start'], form.cleaned_data['end']
                    if recurring == 'd': delta = timedelta(1)
                    elif recurring == 'w': delta = timedelta(7)
                    elif recurring == 'f': delta = timedelta(14)
                    start, end = start + delta, end + delta
                    form.cleaned_data.update({'start':start, 'end':end})
                    # save the form and append the object
                    self.new_objects.append(self.save_new(form, commit))
                    if not commit:
                        self.saved_form.append(form)
        return self.new_objects


class EntryInline(ModelBaseTabularInline):
    model = Entry
    form = EntryInlineForm
    formset = EntryInlineFormSet
    fk_name = 'content'
    extra = 1
"""

class EntryInline(ModelBaseTabularInline):
    model = Entry
    fk_name = 'content'
    exclude = ['labels',]


class EntryAdmin(ModelBaseAdmin):
    list_display = ('start', 'end', 'content',) + ModelBaseAdmin.list_display
    list_filter = ('start', 'end',) + ModelBaseAdmin.list_filter
    search_fields = ('start', 'end',)
    
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)

    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('start', 'end', 'content',)


admin.site.register(Entry, EntryAdmin)
