from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from .models import Task

# Registration form
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'password']

def register_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    error = None
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('task_list')
        else:
            error = "Invalid registration details"
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"form": form, "error": error})

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('task_list')
        else:
            error = "Invalid username or password"
    return render(request, "main/login.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def task_list(request):
    search = request.GET.get('search', '').strip().lower()
    platform = request.GET.get('platform', '')
    location = request.GET.get('location', '')
    date = request.GET.get('date', '')

    tasks = Task.objects.all()
    filtered = tasks
    if search:
        filtered = [t for t in filtered if search in t.name.lower() or search in str(t.id)]
    if platform:
        filtered = [t for t in filtered if t.platform == platform]
    if location:
        filtered = [t for t in filtered if t.location == location]
    if date:
        filtered = [t for t in filtered if t.start_time.startswith(date)]

    platforms = sorted(set(t.platform for t in tasks))
    locations = sorted(set(t.location for t in tasks))

    return render(request, 'main/task_system.html', {
        'tasks': filtered,
        'platforms': platforms,
        'locations': locations,
        'search': request.GET.get('search', ''),
        'selected_platform': platform,
        'selected_location': location,
        'date': date,
        'page': 1,
        'total_pages': 1,
        'page_range': range(1, 2),
    })
