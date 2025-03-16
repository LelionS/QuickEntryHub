from django.contrib import admin
from django.apps import apps
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
