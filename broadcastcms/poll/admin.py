from django.contrib import admin
from models import Poll, PollOption
from broadcastcms.base.admin import ContentBaseAdmin, ModelBaseTabularInline

class PollOptionInline(ModelBaseTabularInline):
    model = PollOption
    fk_name = 'poll'
    exclude = ['labels',]


class PollAdmin(ContentBaseAdmin):
    inlines = (
        PollOptionInline,
    )
    save_on_top = True


admin.site.register(Poll, PollAdmin)
