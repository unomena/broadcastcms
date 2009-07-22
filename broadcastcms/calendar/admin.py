from django import forms
from django.contrib import admin
from models import *
from broadcastcms.base.admin import ModelBaseAdmin, ModelBaseTabularInline


RECURRING_CHOICES = (
    ('d', 'Daily'),
    ('w', 'Weekly'),
    ('m', 'Monthly'),
    ('y', 'Yearly'),
)


class EntryInlineForm(forms.ModelForm):
    recurring = forms.ChoiceField(
        label='Recurring',
        choices=RECURRING_CHOICES,
    )
    recurring_amount = forms.IntegerField(
        label='Recurring Amount',
    )

    def save(self, commit=True):
        return super(EntryInlineForm, self).save(commit)


class EntryInline(ModelBaseTabularInline):
    model = Entry
    form = EntryInlineForm
    fk_name = 'content'
    extra = 1


class EntryAdmin(ModelBaseAdmin):
    list_display = ('start', 'end', 'content', 'is_public')
    list_filter = ('is_public', 'start', 'end', 'content')
    search_fields = ('start', 'end', 'content')


admin.site.register(Entry, EntryAdmin)
