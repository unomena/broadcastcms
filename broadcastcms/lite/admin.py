from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from models import Settings, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserAdmin(UserAdmin):
    inlines = [
        UserProfileInline,
    ]

# Unregister default django User admin 
admin.site.unregister(User)

# Register our customized User admin 
admin.site.register(User, UserAdmin)

admin.site.register(Settings)
