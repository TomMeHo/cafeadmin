from django.contrib import admin
# from shift_planner.models import ShiftRegistration
from datetime import datetime

from . import models

class ShiftAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["date", "title", "starts_at", "ends_at", "required_employees_min", "required_employees_max"],
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

admin.site.register(models.Shift, ShiftAdmin)
admin.site.register(models.ShiftRegistration, ShiftRegistrationAdmin)
admin.site.register(models.Holiday)