from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from datetime import datetime

from .forms import CustomUserCreationForm, CustomUserChangeForm

from . import models


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = models.CustomUser
    list_display = ["email", "username",]

class ShiftAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["shift_date", "title", "starts_at", "ends_at", "required_employees_min", "required_employees_max"],
                # "properties": ["registered_employees"],
            },
        ),
    ]

class ShiftRegistrationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["shift", "registree"],
            },
        ),
        (
            "Administrative fields",
            {
                "classes": ["collapse"],
                "fields": ["registered_at", "registered_by"],
            },
        ),
    ]

    def save_model(self, request, instance, form, change):
        instance.registered_by = request.user
        instance.registered_at = datetime.now()
        instance.save()

admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.Shift, ShiftAdmin)
admin.site.register(models.ShiftRegistration, ShiftRegistrationAdmin)
admin.site.register(models.Holiday)