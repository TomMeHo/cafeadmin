from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShiftPlannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shift_planner'
    verbose_name = _("Shift Planner")