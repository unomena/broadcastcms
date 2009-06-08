from django import forms
from django.contrib import admin
from broadcastcms.shortcuts import comma_seperated_admin_links
from broadcastcms.label.models import Label

def comma_seperated_admin_label_links(obj):
    return comma_seperated_admin_links(obj.labels.all())

comma_seperated_admin_label_links.short_description = 'Labels'
comma_seperated_admin_label_links.allow_tags = True

class ContentBaseAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContentBaseAdminForm, self).__init__(*args, **kwargs)
        self.fields['labels'].choices = self.get_label_choices('labels')

    def get_label_choices(self, field_name):
        labels = Label.objects.filter(restricted_to__contains='%s-%s' % (self._meta.model._meta.object_name.lower(), field_name))
        choices = []
        for label in labels:
            choices.append((label.id, str(label)))
        return choices

class ContentBaseAdmin(admin.ModelAdmin):
    form = ContentBaseAdminForm

    list_display = ('title', 'description', comma_seperated_admin_label_links, 'created', 'modified', 'is_public')
    list_filter = ('labels', 'is_public', 'created', 'modified')
    search_fields = ('title', 'description', 'content')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'is_public')}),
        ('Labels', {'fields': ('labels',),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('image', 'created',),
                  'classes': ('collapse',),
        }),
    )
