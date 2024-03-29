from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required

from datetime import datetime, timedelta, date

from .models import Shift, ShiftRegistration, CalendarWeek, CalendarMonth, CustomUser
from .constants import APP_DISPLAY_NAME

# TODO remove
@login_required(login_url='/accounts/login/')
def list_shifts(request):
    shifts = Shift.objects.order_by("shift_date")
    return render(request, "shifts/list.html", _get_shift_list_context(request, shifts))


# TODO improve
@login_required(login_url='/accounts/login/')
@permission_required('shift_planner.does_planning')
def shift_detail(request, shift_id):
    shift = get_object_or_404(Shift, pk=shift_id)
    registrations = ShiftRegistration.objects.filter(shift=shift_id)
    
    registered_usernames = [ x.registree for x in registrations ]
    all_users = CustomUser.objects.all().order_by('last_name')
    not_registered_users = [x for x in all_users if x not in registered_usernames]

    return render(request, "shifts/detail.html", {"shift": shift, "registrations": registrations, "not_registered_users": not_registered_users, "nav_menu_item": "detail"})


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


@permission_required('shift_planner.can_register_others')
@login_required(login_url='/accounts/login/')
def shift_unregister_other(request, shift_id, employee_id):
    shift = Shift.objects.get(pk=shift_id)
    employee = CustomUser.objects.get(id=employee_id)
    shift.unregister(employee)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@permission_required('shift_planner.can_register_others')
@login_required(login_url='/accounts/login/')
def shift_register_other(request, shift_id, employee_id):
    shift = Shift.objects.get(pk=shift_id)
    employee = CustomUser.objects.get(id=employee_id)
    shift.register(employee)
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
        Q(shift_date__gte = datetime.today())
    ).order_by("shift_date", "starts_at")[:3]

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