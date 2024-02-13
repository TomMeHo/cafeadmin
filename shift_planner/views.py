from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from datetime import datetime, timedelta, date

from .models import Shift, ShiftRegistration, CalendarWeek, CalendarMonth
from .constants import APP_DISPLAY_NAME

# TODO remove
@login_required(login_url='/accounts/login/')
def list_shifts(request):
    shifts = Shift.objects.order_by("date")
    return render(request, "shifts/list.html", _get_shift_list_context(request, shifts))

# TODO improve
@login_required(login_url='/accounts/login/')
def shift_detail(request, shift_id):
    shift = get_object_or_404(Shift, pk=shift_id)
    registrations = ShiftRegistration.objects.filter(shift=shift_id)
    return render(request, "shifts/detail.html", {"shift": shift, "registrations": registrations})

@login_required(login_url='/accounts/login/')
def shift_register_myself(request, shift_id):
    if request.user.is_authenticated:
        shift = Shift.objects.get(pk=shift_id)
        shift.register(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
#TODO provide a notification
    
@login_required(login_url='/accounts/login/')
def shift_unregister_myself(request, shift_id):
    if request.user.is_authenticated:
        shift = Shift.objects.get(pk=shift_id)
        shift.unregister(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required(login_url='/accounts/login/')
def shift_by_month(request, year = 0, month = 0):
    # TODO check for user authenticated
    year = datetime.now().year if year == 0 else year
    month = datetime.now().month if month == 0 else month
    firstday = date(year, month, 1)

    calendarMonth = CalendarMonth.getMonth( month, year, request.user )

    calendarMonth.month = month
    calendarMonth.year = year

    context = { "first_day": firstday,
                "previous": { 
                    "year": (firstday - timedelta(days=1)).year, 
                    "month": (firstday - timedelta(days=1)).month 
                },
                "next": {
                    "year": (firstday + timedelta(days=1)).year, 
                    "month": (firstday + timedelta(days=31)).month
                },
                "month": calendarMonth,
                "nav_menu_item": "by_month" }

    return render(request, "shifts/monthly.html", context)
       
@staticmethod
def _add_constants(context):
    context += { "application_display_name": APP_DISPLAY_NAME }

# TODO remove
# def shift_my(request):
#     shifts = []
#     if request.user.is_authenticated:
#         shifts = Shift.objects.filter(registree = request.user).order_by("date")
#     return render(request, "shifts/list.html", _get_shift_list_context(request, shifts))

def _get_shift_list_context(request, shifts):
    username = 'None'
    if request.user.is_authenticated:
        username = request.user.username
        for shift in shifts:
            shift.is_registered = shift.is_registered(request.user)
    context = {"shifts": shifts, "user": username, "is_authenticated": request.user.is_authenticated}
    return context

@login_required(login_url='/accounts/login/')
def overview(request):
    # TODO check that user is registered, otherwise to other endpoint

    my_next_shifts = Shift.objects.filter(
        Q(shiftregistration__registree = request.user.id),
        Q(date__gte = datetime.today())
    ).order_by("date", "starts_at")[:3]

    for shift in my_next_shifts:
        shift.is_registered = shift.is_registered(request.user)

    next_weeks = []
    next_weeks.append(CalendarWeek.getSpecificWeek(datetime.today().date(), request.user))
    next_weeks.append(CalendarWeek.getSpecificWeek(datetime.today().date() + timedelta(days=7), request.user))

    context = {"my_next_shifts": my_next_shifts, "next_weeks": next_weeks, "nav_menu_item": "overview"}
    return render(request, "shifts/overview.html", context)

# def logout(request):
#     logout(request)
#     # TODO redirect

# def login(request):
#     username = request.POST["id_username"]
#     password = request.POST["id_password"]
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         # Redirect to a success page.
#         ...
#     else:
#         # Return an 'invalid login' error message.
#         ...