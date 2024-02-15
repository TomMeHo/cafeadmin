from typing import Self

from django.db import models
from django.db.models import Count
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta, datetime
from calendar import monthrange, month


from .constants import UNREGISTER_MIN_BEFORE_DAYS

class CustomUser(AbstractUser):
    pass
    # add additional fields in here

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "User"

class Shift(models.Model):
    shift_date = models.DateField(verbose_name = _("Date"))
    starts_at = models.TimeField(verbose_name = _("Starts at"))
    ends_at = models.TimeField(verbose_name = _("Ends at"))
    title = models.CharField(max_length = 80, default = '', verbose_name = _("Title"), blank=False)
    required_employees_min = models.IntegerField(default = 0, verbose_name = _("Minimum required employees"))
    required_employees_max = models.IntegerField(default = 0, verbose_name = _("Maximum required employees"))

    class Meta:
        verbose_name = "Schicht"
        verbose_name_plural = "Schichten"
        permissions = (("can_register_others", "Register other users"),
                       ("does_planning", "Sees planning relevant details"),)

    def __str__(self):
        dFormat = '%d.%m.%y'
        tFormat = '%H:%M'
        return f"{self.shift_date.strftime(dFormat)}, {self.starts_at.strftime(tFormat)}-{self.ends_at.strftime(tFormat)}: {self.title}"

    @property
    def unregister_possible(self):
        last_unregister_date = self.shift_date - timedelta(days = UNREGISTER_MIN_BEFORE_DAYS)
        today = datetime.now().date()
        is_possible = True if today < last_unregister_date else False
        return is_possible

    @property
    def is_past(self):
        start_date = datetime.combine(self.shift_date, self.starts_at)
        return ( start_date < datetime.now() )

    @property
    def registered_employees(self):
        registrations = ShiftRegistration.objects.filter(shift = self)
        return registrations.count()

    def is_registered(self, user: CustomUser):
        registration = ShiftRegistration.objects.filter(shift = self, registree = user)
        return True if registration.count() > 0 else False

    def register(self, user: CustomUser):
        if self.is_registered(user) == False:
            registration = ShiftRegistration(shift = self, registree = user)
            registration.save()

    def unregister(self, user: CustomUser):
        registrations = ShiftRegistration.objects.filter(shift=self, registree=user)
        registrations.delete()

    @staticmethod
    def get_shifts_by_user(user: CustomUser):
        return Shift.objects.filter(registree=user)
    
    # TODO remove
    # @staticmethod
    # def get_shifts_for_range(date_from: date, date_to: date):
    #     shifts = Shift.objects.filter(shift_date__gte = date_from, shift_date__lte = date_to)
    #     holidays = Holiday.objects.filter(shift_date__gte = date_from, shift_date__lte = date_to)
    #     days = []
    #     delta = timedelta( days = 1 )

    #     while( date_from <= date_to ):
    #         holiday = holidays.filter(shift_date=date_from)
    #         shifts_for_date = shifts.filter(shift_date = date_from).order_by('starts_at')

    #         days.append( CalendarDay( date_from, holiday, shifts_for_date ) )
    #         date_from += delta
    #     return days

class ShiftRegistration(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.DO_NOTHING)
    registree = models.ForeignKey(CustomUser, related_name='user_registree', on_delete=models.CASCADE, default='')
    registered_at = models.DateTimeField(null = True, blank = True)
    registered_by = models.ForeignKey(CustomUser, related_name='user_registered_by', on_delete=models.DO_NOTHING, null = True, blank = True)

    class Meta:
        verbose_name = "Schichtanmeldung"
        verbose_name_plural = "Schichtanmeldungen"

class Holiday(models.Model):
    date = models.DateField(primary_key=True)
    name = models.CharField(max_length = 40, default = '')

    class Meta:
        verbose_name = "Feiertag"
        verbose_name_plural = "Feiertage"

    def __str__(self):
        dFormat = '%d.%m.%y'
        return f"{self.date.strftime(dFormat)} - {self.name}"


class CalendarDay:
    def __init__(self, day : date, holiday : Holiday, shifts):
        self.date = day
        self.holiday = holiday
        self.shifts = shifts
        now = datetime.today().date()
        self.is_past = False if day > now else True

    @staticmethod
    def getSpecificDay(specific_date : date, user : CustomUser) -> Self:
        shifts = Shift.objects.filter(shift_date = specific_date).order_by('starts_at')
        for shift in shifts:
            shift.is_registered = shift.is_registered(user)

        holidays = Holiday.objects.filter(date = specific_date)
        return CalendarDay( day=specific_date, holiday=holidays.first(), shifts=shifts )

class CalendarWeek:
    def __init__(self, monday : date, days : list[CalendarDay]):
        self.monday = monday
        self.sunday = monday + timedelta(days = 6)
        self.weeknum = monday.isocalendar()[1]
        self.days = days
    
    @staticmethod
    def getSpecificWeek(any_day_of_week : date, user : CustomUser) -> Self:
        weekday = datetime(any_day_of_week.year, any_day_of_week.month, any_day_of_week.day).weekday()
        monday = any_day_of_week - timedelta(days = weekday)
        sunday = monday + timedelta(days = 6)
        days = []
        day = monday
        
        while( day <= sunday ):
            days.append( CalendarDay.getSpecificDay(day, user) )
            day += timedelta(days=1)

        return CalendarWeek(monday=monday, days=days)
    
class CalendarMonth:
    def __init__(self, month : int, year : int, weeks : list[CalendarWeek]):
        self.month = month
        self.year = year
        self.weeks = weeks

    @staticmethod
    def getMonth(month : int, year : int, user : CustomUser):
        # TODO remove user parameter
        weeks = []

        firstday = date(year, month, day = 1)
        last_day = date(year, month, day = 1) + timedelta(days = monthrange(year, month)[1] - 1)
        day = firstday

        while day <= last_day:
            weeks.append(CalendarWeek.getSpecificWeek(day, user))
            day += timedelta(days=7)

        return CalendarMonth(month, year, weeks)