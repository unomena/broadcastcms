from django import forms
from django.contrib import admin
from django.db.models import get_apps, get_models

from models import Label

class LabelAdminForm(forms.ModelForm):
    restricted_to = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        super(LabelAdminForm, self).__init__(*args, **kwargs)
        self.fields['restricted_to'].choices = self.get_label_choices()

    def get_label_choices(self):
        choices = []
        apps = get_apps()
        for app in apps:
            for model in get_models(app):
                for many_to_many in model._meta.many_to_many:
                    if many_to_many.rel.to == Label:
                        choices.append(("%s-%s" % (model._meta.module_name, many_to_many.name), "%s - %s" % (model._meta.verbose_name.title(), many_to_many.name.title())))

        return choices

class LabelAdmin(admin.ModelAdmin):
    form = LabelAdminForm
    list_display = ('title', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('title',)

admin.site.register(Label, LabelAdmin)
