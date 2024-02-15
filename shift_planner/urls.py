from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from . import views

app_name = "planner"
urlpatterns = [
    # path('', views.overview, name = 'index'),
    path('', views.overview, name = 'overview'),
    path('shift/<int:shift_id>', views.shift_detail),
    path('shift/<int:shift_id>/register', views.shift_register_myself),
    path('shift/<int:shift_id>/register/<int:employee_id>', views.shift_register_other),
    path('shift/<int:shift_id>/unregister', views.shift_unregister_myself),
    path('shift/<int:shift_id>/unregister/<int:employee_id>', views.shift_unregister_other),
    path('monthly', views.shift_by_month, name='monthly'),
    path('monthly/', views.shift_by_month),
    path('monthly/<int:year>/<int:month>', views.shift_by_month),
]