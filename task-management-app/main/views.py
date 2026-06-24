from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Task, UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
import re
from .forms import TaskForm, RegisterForm
from .decorators import admin_required

def register_view(request):
    error = None
    if request.method == "POST":
        form = RegisterForm(request.POST)
        name = request.POST.get("name", "").strip()
        # default role is client; only superusers can create admins
        role = 'client'
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if User.objects.filter(username=username).exists():
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
                # If the request is by a logged-in superuser and explicitly requested admin, allow it
                requested_role = request.POST.get('role', 'client')
                if request.user.is_authenticated and request.user.is_superuser and requested_role == 'admin':
                    role = 'admin'
                UserProfile.objects.create(user=user, role=role)
                return redirect(reverse('login') + '?registered=1')
        else:
            error = form.errors.as_json()
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"error": error, 'form': form})

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

    # Order for deterministic pagination and derive dropdown values from filtered queryset
    tasks = tasks.order_by('id')

    paginator = Paginator(tasks, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Derive dropdown values from the current page to avoid showing unrelated items
    page_tasks = list(page_obj.object_list)
    def unique(seq, key=lambda x: x):
        seen = set()
        out = []
        for v in seq:
            k = key(v)
            if k not in seen:
                seen.add(k)
                out.append(k)
        return out

    titles = unique(page_tasks, key=lambda t: t.title)
    platforms = unique(page_tasks, key=lambda t: t.platform)
    locations = unique(page_tasks, key=lambda t: t.location)
    statuses = unique(page_tasks, key=lambda t: t.status)
    start_times = unique(page_tasks, key=lambda t: t.start_time)
    end_times = unique(page_tasks, key=lambda t: t.end_time)
    retries_list = unique(page_tasks, key=lambda t: t.retries)

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
    task = get_object_or_404(Task, id=task_id)
    error = None
    if request.method == "POST":
        if not (request.user.is_superuser or getattr(getattr(request.user, 'userprofile', None), 'role', '') == 'admin'):
            return redirect('task_list')
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
        else:
            error = form.errors
    else:
        form = TaskForm(instance=task)
    return render(request, "main/task_form.html", {"form": form, "task": task, "error": error, "action": "Edit"})

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
@require_POST
def delete_task(request, task_id):
    if not (request.user.is_superuser or getattr(getattr(request.user, 'userprofile', None), 'role', '') == 'admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied.'})
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return JsonResponse({'success': True})

@login_required
def add_task(request):
    error = None
    if request.method == "POST":
        # Only admins can add tasks
        if not (request.user.is_superuser or getattr(getattr(request.user, 'userprofile', None), 'role', '') == 'admin'):
            return redirect('task_list')
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            return redirect('task_list')
        else:
            error = form.errors
    else:
        form = TaskForm()
    return render(request, "main/task_form.html", {"form": form, "error": error, "action": "Add"})

@require_POST
@login_required
def ajax_cancel_task(request, task_id):
    from .models import Task
    task = get_object_or_404(Task, id=task_id)
    # Only allow admin to cancel
    if not (request.user.is_superuser or getattr(getattr(request.user, 'userprofile', None), 'role', '') == 'admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    task.status = 'cancelled'
    task.save()
    return JsonResponse({
        'success': True,
        'task_id': task.id,
        'new_status': task.status,
    })
