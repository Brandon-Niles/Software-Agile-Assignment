from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/cancel/', views.cancel_task, name='cancel_task'),
    path('ajax/cancel-task/<int:task_id>/', views.ajax_cancel_task, name='ajax_cancel_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
]