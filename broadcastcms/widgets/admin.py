from copy import deepcopy

from django.contrib import admin

from broadcastcms.base.admin import ModelBaseAdmin, ModelBaseTabularInline

from models import AccountMenuWidget, BannerWidget, FacebookSetupWidget, FriendsWidget, FriendsSideNavWidget, NowPlayingWidget, OnAirWidget, SlidingPromoWidget, SlidingPromoWidgetSlot

class SlidingPromoWidgetSlotInline(ModelBaseTabularInline):
    model = SlidingPromoWidgetSlot
    fk_name = 'widget'

class SlidingPromoWidgetAdmin(ModelBaseAdmin):
    list_display = ('title',) + ModelBaseAdmin.list_display
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('title',)

    inlines = (
        SlidingPromoWidgetSlotInline,
    )

admin.site.register(AccountMenuWidget)
admin.site.register(BannerWidget)
admin.site.register(FacebookSetupWidget)
admin.site.register(FriendsWidget)
admin.site.register(FriendsSideNavWidget)
admin.site.register(NowPlayingWidget)
admin.site.register(OnAirWidget)
admin.site.register(SlidingPromoWidget, SlidingPromoWidgetAdmin)
