from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import sample, Profile

from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

app_models = apps.get_app_config('samples').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass

#admin.site.register(sample)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    
    
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

