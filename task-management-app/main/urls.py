from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),  # Root URL shows login page
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('tasks/', views.task_list, name='task_list'),
]