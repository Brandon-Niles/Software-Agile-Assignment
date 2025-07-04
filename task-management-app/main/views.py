from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from .models import Task, UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
import re

# Registration form
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'password']

def register_view(request):
    error = None
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        role = request.POST.get("role", "client")

        # Password validation: at least 8 chars, 1 uppercase, 1 lowercase, 1 digit
        if len(password) < 8 or \
           not re.search(r'[A-Z]', password) or \
           not re.search(r'[a-z]', password) or \
           not re.search(r'\d', password):
            error = "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, and a digit."
        elif not (name and username and email and password and role):
            error = "All fields are required."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        elif User.objects.filter(email=email).exists():
            error = "Email already exists."
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name
            )
            UserProfile.objects.create(user=user, role=role)
            return redirect(reverse('login') + '?registered=1')
    return render(request, "main/register.html", {"error": error})

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Always fetch or create UserProfile and set role accordingly
            try:
                profile = user.userprofile
            except UserProfile.DoesNotExist:
                # Fallback: create as client
                profile = UserProfile.objects.create(user=user, role='client')
            request.session['selected_role'] = profile.role
            return redirect('task_list')
        else:
            error = "Invalid username or password."
    return render(request, "main/login.html", {"error": error})

def logout_view(request):
    logout(request)
    request.session.pop('selected_role', None)
    return redirect('login')

@login_required
def task_list(request):
    search = request.GET.get('search', '').strip()
    tasks = Task.objects.all()

    # Filtering by dropdowns
    title = request.GET.get('title', '')
    platform = request.GET.get('platform', '')
    location = request.GET.get('location', '')
    status = request.GET.get('status', '')
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')
    retries = request.GET.get('retries', '')

    if title:
        tasks = tasks.filter(title=title)
    if platform:
        tasks = tasks.filter(platform=platform)
    if location:
        tasks = tasks.filter(location=location)
    if status:
        tasks = tasks.filter(status=status)
    if start_time:
        tasks = tasks.filter(start_time=start_time)
    if end_time:
        tasks = tasks.filter(end_time=end_time)
    if retries:
        tasks = tasks.filter(retries=retries)

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

    # Get unique values for dropdowns
    titles = Task.objects.values_list('title', flat=True).distinct()
    platforms = Task.objects.values_list('platform', flat=True).distinct()
    locations = Task.objects.values_list('location', flat=True).distinct()
    statuses = Task.objects.values_list('status', flat=True).distinct()
    start_times = Task.objects.values_list('start_time', flat=True).distinct()
    end_times = Task.objects.values_list('end_time', flat=True).distinct()
    retries_list = Task.objects.values_list('retries', flat=True).distinct()

    paginator = Paginator(tasks, 50) 
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    selected_role = request.session.get('selected_role', '')

    context = {
        'tasks': page_obj.object_list,
        'page_obj': page_obj,
        'search': search,
        'selected_role': selected_role,
        'titles': titles,
        'platforms': platforms,
        'locations': locations,
        'statuses': statuses,
        'start_times': start_times,
        'end_times': end_times,
        'retries': retries_list,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('main/task_table_rows.html', {
            **context,
            'user': request.user,
        })
        return JsonResponse({'html': html})

    return render(request, 'main/task_system.html', context)

@login_required
def edit_task(request, task_id):
    if not request.user.is_superuser:
        return redirect('task_list')
    task = get_object_or_404(Task, id=task_id)
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
        return redirect('task_list')
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.status = 'Cancelled'
        task.save()
        return redirect('task_list')
    return render(request, 'main/cancel_task.html', {'task': task})

@login_required
def delete_task(request, task_id):
    selected_role = request.session.get('selected_role', '')
    if selected_role != 'admin':
        messages.error(request, "Only admins can delete tasks.")
        return redirect('task_list')
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect('task_list')
    return redirect('task_list')

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

@require_POST
@login_required
def ajax_cancel_task(request, task_id):
    from .models import Task
    task = get_object_or_404(Task, id=task_id)
    # Only allow admin to cancel
    if request.session.get('selected_role') != 'admin':
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    task.status = 'cancelled'
    task.save()
    return JsonResponse({
        'success': True,
        'task_id': task.id,
        'new_status': task.status,
    })
