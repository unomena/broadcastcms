from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.auth.models import User

from broadcastcms.shortcuts import comma_seperated_admin_links
from broadcastcms.label.models import Label

def restrict_fieldsets(request, fieldsets):
    """
    Removes fields user does not have privileges to edit.
    For now we simply remove the is_public field for non superusers.
    """
    if request.user.is_superuser:
        return fieldsets

    for fieldset in fieldsets:
        for item in fieldset:
            if item.__class__ == dict:
                if item.has_key('fields'):
                    if 'is_public' in item['fields']:
                        fields = list(item['fields'])
                        fields.remove('is_public')
                        item['fields'] = tuple(fields)
        return fieldsets

class ModelBaseInlineModelAdmin(InlineModelAdmin):
        
    def get_fieldsets(self, request, obj=None):
        "Hook for specifying fieldsets."
        if self.declared_fieldsets:
            fieldsets = self.declared_fieldsets
        else:
            form = self.get_formset(request).form
            fieldsets = [(None, {'fields': form.base_fields.keys()})]
        return restrict_fieldsets(request, fieldsets)


class ModelBaseStackedInline(ModelBaseInlineModelAdmin, admin.StackedInline):
    pass

class ModelBaseTabularInline(ModelBaseInlineModelAdmin, admin.TabularInline):
    pass

class ModelBaseAdmin(admin.ModelAdmin):

    def get_fieldsets(self, request, obj=None):
        "Hook for specifying fieldsets."
        if self.declared_fieldsets:
            fieldsets = self.declared_fieldsets
        else:
            form = self.get_form(request, obj)
            fieldsets = [(None, {'fields': form.base_fields.keys()})]
        return restrict_fieldsets(request, fieldsets)

def comma_seperated_admin_label_links(obj):
    return comma_seperated_admin_links(obj.labels.all())

comma_seperated_admin_label_links.short_description = 'Labels'
comma_seperated_admin_label_links.allow_tags = True

class ContentBaseAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContentBaseAdminForm, self).__init__(*args, **kwargs)
        self.fields['labels'].choices = self.get_label_choices('labels')
        #self.fields['owner'].choices = self.get_owner_choices()

    def get_label_choices(self, field_name):
        labels = Label.objects.filter(restricted_to__contains='%s-%s' % (self._meta.model._meta.object_name.lower(), field_name))
        choices = []
        for label in labels:
            choices.append((label.id, str(label)))
        return choices

    def get_owner_choices(self):
        choices = []
        for user in User.objects.filter(is_staff=True):
            choices.append((user.id, str(user)))
        return choices


class ContentBaseAdmin(ModelBaseAdmin):
    form = ContentBaseAdminForm

    list_display = ('title', 'description', comma_seperated_admin_label_links, 'created', 'modified', 'is_public')
    list_filter = ('labels', 'is_public', 'created', 'modified')
    search_fields = ('title', 'description', 'content')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'rating', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created', 'owner'),
                  'classes': ('collapse',),
        }),
    )
   
    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
            obj.save()
        return super(ContentBaseAdmin, self).save_model(request, obj, form, change)
