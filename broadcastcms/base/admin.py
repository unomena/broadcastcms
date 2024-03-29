from copy import deepcopy

from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.auth.models import User
from django.db.models import get_model

from broadcastcms.shortcuts import comma_seperated_admin_links
from broadcastcms.label.models import Label

def comma_seperated_admin_label_links(obj):
    return comma_seperated_admin_links(obj.labels.all())

comma_seperated_admin_label_links.short_description = 'Labels'
comma_seperated_admin_label_links.allow_tags = True

def restrict_fieldsets(request, fieldsets):
    """
    Removes fields user does not have privileges to edit.
    For now we simply remove the is_public field for non superusers and non owners.
    """
    if request.user.is_superuser:
        return fieldsets
    
    app, model, pk = request.path.split('/')[-4:-1]
    if pk == 'add':
        return fieldsets

    model = get_model(app, model)
    instance = model.objects.get(pk=pk)
    owner = (request.user == instance.owner)

    if owner:
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


class ModelBaseAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModelBaseAdminForm, self).__init__(*args, **kwargs)
        self.fields['labels'].choices = self.get_label_choices('labels')

    def get_label_choices(self, field_name):
        labels = Label.objects.filter(restricted_to__contains='%s-%s' % (self._meta.model._meta.object_name.lower(), field_name))
        choices = []
        for label in labels:
            choices.append((label.id, str(label)))
        return choices


class ModelBaseAdmin(admin.ModelAdmin):
    
    form = ModelBaseAdminForm
    list_display = (comma_seperated_admin_label_links, 'is_public')
    list_filter = ('labels', 'is_public',)
    fieldsets = (
        (None, {'fields': ('is_public',)}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        "Hook for specifying fieldsets."
        if self.declared_fieldsets:
            fieldsets = self.declared_fieldsets
        else:
            form = self.get_form(request, obj)
            fieldsets = [(None, {'fields': form.base_fields.keys()})]
        return restrict_fieldsets(request, fieldsets)
    

class ContentBaseAdminForm(ModelBaseAdminForm):

    def __init__(self, *args, **kwargs):
        super(ContentBaseAdminForm, self).__init__(*args, **kwargs)
        #self.fields['owner'].choices = self.get_owner_choices()

    def get_owner_choices(self):
        choices = []
        for user in User.objects.filter(is_staff=True):
            choices.append((user.id, str(user)))
        return choices


class ContentBaseAdmin(ModelBaseAdmin):
    form = ContentBaseAdminForm

    list_display = ('title', 'owner', 'created', 'modified',) + ModelBaseAdmin.list_display
    list_filter = ('created', 'modified',) + ModelBaseAdmin.list_filter
    search_fields = ('title', 'description', 'content')
    
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('title', 'description',)

    fieldsets += (
        ('Meta', {'fields': ('image', 'created', 'owner', 'rating',),
                  'classes': ('collapse',),
        }),
    )
   
    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
            obj.save()
        return super(ContentBaseAdmin, self).save_model(request, obj, form, change)
