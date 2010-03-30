from copy import deepcopy

from django import forms
from django.contrib import admin

from broadcastcms.base.admin import ContentBaseAdmin
from models import Post

from tinymce.widgets import TinyMCE

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Post

class PostAdmin(ContentBaseAdmin):
    form = PostAdminForm
    fieldsets = deepcopy(ContentBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('content',)

admin.site.register(Post, PostAdmin)
