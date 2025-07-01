from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from .models import Task
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.template.loader import render_to_string

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
    search = request.GET.get('search', '').strip()
    tasks = Task.objects.all()
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) |
            Q(platform__icontains=search) |
            Q(location__icontains=search) |
            Q(status__icontains=search) |
            Q(start_time__icontains=search) |
            Q(end_time__icontains=search) |
            Q(retries__icontains=search)
        )
    paginator = Paginator(tasks, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('main/task_table_rows.html', {
            'tasks': page_obj.object_list,
            'page_obj': page_obj,
            'user': request.user,
            'search': search,
        })
        return JsonResponse({'html': html})

    return render(request, 'main/task_system.html', {
        'tasks': page_obj.object_list,
        'page_obj': page_obj,
        'search': search,
    })

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not request.user.is_superuser:
        return redirect('task_list')
    if request.method == 'POST':
        task.title = request.POST.get('title', task.title)
        task.platform = request.POST.get('platform', task.platform)
        task.location = request.POST.get('location', task.location)
        task.status = request.POST.get('status', task.status)
        task.start_time = request.POST.get('start_time', task.start_time)
        task.end_time = request.POST.get('end_time', task.end_time)
        task.retries = request.POST.get('retries', task.retries)
        task.save()
        return redirect('task_list')
    return render(request, 'main/edit_task.html', {'task': task})

@login_required
def cancel_task(request, task_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.status = 'Cancelled'
        task.save()
        return redirect('task_list')
    return render(request, 'main/cancel_task.html', {'task': task})

@login_required
def add_task(request):
    if not request.user.is_superuser:
        return redirect('task_list')
    if request.method == 'POST':
        Task.objects.create(
            title=request.POST.get('title', 'System Update'),
            platform=request.POST.get('platform', ''),
            location=request.POST.get('location', ''),
            status=request.POST.get('status', ''),
            start_time=request.POST.get('start_time', ''),
            end_time=request.POST.get('end_time', ''),
            retries=request.POST.get('retries', 0)
        )
        return redirect('task_list')
    return render(request, 'main/add_task.html')
