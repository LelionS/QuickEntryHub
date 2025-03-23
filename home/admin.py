from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import Bay, Bed, Variety

# Define models that will be explicitly registered
explicit_models = {Bay, Bed, Variety}

# Automatically register all models in the 'home' app, except the ones explicitly registered
app_models = apps.get_app_config('home').get_models()
for model in app_models:
    if model in explicit_models:
        continue  # Skip models that are explicitly registered
    if model not in admin.site._registry:
        admin.site.register(model)

# Define an admin action to deactivate users
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_users.short_description = "Deactivate selected users"

# Extend UserAdmin to include the action and styling
class CustomUserAdmin(UserAdmin):
    actions = [deactivate_users]

    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',  # Example: Font Awesome
                    '/static/admin/css/custom_admin.css',)  # Link to custom CSS (place in static folder)
        }
        js = ('/static/admin/js/custom_admin.js',)  # Link to custom JS (optional)

# Unregister default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class VarietyInline(admin.TabularInline):
    model = Variety
    extra = 1

class BedInline(admin.TabularInline):
    model = Bed
    extra = 1
    inlines = [VarietyInline]

@admin.register(Bay)
class BayAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [BedInline]

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("code", "bay")
    search_fields = ("code",)
    list_filter = ("bay",)
    inlines = [VarietyInline]

@admin.register(Variety)
class VarietyAdmin(admin.ModelAdmin):
    list_display = ("name", "bed")
    search_fields = ("name",)
    list_filter = ("bed",)
