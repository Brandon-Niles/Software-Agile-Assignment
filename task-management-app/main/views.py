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
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
import os
from pathlib import Path
from django.contrib.admin.views.decorators import staff_member_required


def user_is_admin(user):
    try:
        if not user or not user.is_authenticated:
            return False
        # superusers should be considered admins as well
        if getattr(user, 'is_superuser', False):
            return True
        return getattr(user.userprofile, 'role', '') == 'admin'
    except ObjectDoesNotExist:
        return False
    except Exception:
        return False


class _EmptyTaskObj:
    def __init__(self):
        self.id = None
        self.title = ''
        self.platform = ''
        self.location = ''
        self.status = ''
        self.start_time = ''
        self.end_time = ''
        self.retries = 0

def register_view(request):
    error = None
    if request.method == "POST":
        form = RegisterForm(request.POST)
        # default role is client; only superusers can create admins
        role = 'client'
        if form.is_valid():
            name = form.cleaned_data.get('first_name', '').strip()
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

    all_tasks = Task.objects.all()
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
        'total_count': all_tasks.count(),
        'pending_count': all_tasks.filter(status__iexact='pending').count(),
        'running_count': all_tasks.filter(status__iexact='running').count(),
        'completed_count': all_tasks.filter(status__iexact='completed').count(),
        'cancelled_count': all_tasks.filter(status__iexact='cancelled').count(),
    }

    # Read application version from VERSION file if present
    try:
        base = Path(__file__).resolve().parents[1]
        version_file = base / 'VERSION'
        if version_file.exists():
            context['app_version'] = version_file.read_text().strip()
        else:
            context['app_version'] = '0.0.0'
    except Exception:
        context['app_version'] = '0.0.0'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('main/task_table_rows.html', {
            **context,
            'user': request.user,
        })
        return JsonResponse({'html': html})

    return render(request, 'main/task_system.html', context)


@login_required
@never_cache
def api_stats(request):
    """Return JSON with simple task statistics for dashboard charts."""
    all_tasks = Task.objects.all()
    data = {
        'total': all_tasks.count(),
        'by_status': {
            'Pending': all_tasks.filter(status__iexact='pending').count(),
            'Running': all_tasks.filter(status__iexact='running').count(),
            'Completed': all_tasks.filter(status__iexact='completed').count(),
            'Cancelled': all_tasks.filter(status__iexact='cancelled').count(),
            'Failed': all_tasks.filter(status__iexact='failed').count(),
        }
    }
    return JsonResponse(data)

    return render(request, 'main/task_system.html', context)


@login_required
def dashboard_view(request):
    # reuse summary stats from task_list but lighter
    all_tasks = Task.objects.all()
    context = {
        'total_count': all_tasks.count(),
        'pending_count': all_tasks.filter(status__iexact='pending').count(),
        'running_count': all_tasks.filter(status__iexact='running').count(),
        'completed_count': all_tasks.filter(status__iexact='completed').count(),
        'cancelled_count': all_tasks.filter(status__iexact='cancelled').count(),
        'app_version': Path(__file__).resolve().parents[1].joinpath('VERSION').read_text().strip() if Path(__file__).resolve().parents[1].joinpath('VERSION').exists() else '0.0.0'
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('main/partials/dashboard_fragment.html', context, request=request)
        return HttpResponse(html)
    return render(request, 'main/tabs/dashboard.html', context)


@login_required
def tasks_page(request):
    # Build the same context as task_list but return a fragment for AJAX requests
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

    tasks = tasks.order_by('id')
    paginator = Paginator(tasks, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    page_tasks = list(page_obj.object_list)
    def unique(seq, key=lambda x: x):
        seen = set(); out = []
        for v in seq:
            k = key(v)
            if k not in seen:
                seen.add(k); out.append(k)
        return out

    titles = unique(page_tasks, key=lambda t: t.title)
    platforms = unique(page_tasks, key=lambda t: t.platform)
    locations = unique(page_tasks, key=lambda t: t.location)
    statuses = unique(page_tasks, key=lambda t: t.status)
    start_times = unique(page_tasks, key=lambda t: t.start_time)
    end_times = unique(page_tasks, key=lambda t: t.end_time)
    retries_list = unique(page_tasks, key=lambda t: t.retries)

    selected_role = request.session.get('selected_role', '')

    all_tasks = Task.objects.all()
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
        'total_count': all_tasks.count(),
        'pending_count': all_tasks.filter(status__iexact='pending').count(),
        'running_count': all_tasks.filter(status__iexact='running').count(),
        'completed_count': all_tasks.filter(status__iexact='completed').count(),
        'cancelled_count': all_tasks.filter(status__iexact='cancelled').count(),
    }

    try:
        base = Path(__file__).resolve().parents[1]
        version_file = base / 'VERSION'
        if version_file.exists():
            context['app_version'] = version_file.read_text().strip()
        else:
            context['app_version'] = '0.0.0'
    except Exception:
        context['app_version'] = '0.0.0'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('main/partials/tasks_fragment.html', context, request=request)
        return HttpResponse(html)
    return render(request, 'main/tabs/tasks.html', context)


@staff_member_required
def users_page(request):
    users = User.objects.all().order_by('-date_joined')[:200]
    context = {'users': users}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse(render_to_string('main/partials/users_fragment.html', context, request=request))
    return render(request, 'main/tabs/users.html', context)


@login_required
def reports_page(request):
    context = {}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse(render_to_string('main/partials/reports_fragment.html', context, request=request))
    return render(request, 'main/tabs/reports.html', context)


@login_required
def settings_page(request):
    context = {}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse(render_to_string('main/partials/settings_fragment.html', context, request=request))
    return render(request, 'main/tabs/settings.html', context)

@admin_required
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    # Immediate admin check to avoid executing any edit logic for non-admins
    if not user_is_admin(request.user):
        return redirect('task_list')
    error = None
    if request.method == "POST":
        # Final permission check before saving
        if not user_is_admin(request.user):
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
    if not user_is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Permission denied.'})
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return JsonResponse({'success': True})

@login_required
def add_task(request):
    # Immediate admin check to avoid executing any add logic for non-admins
    if not user_is_admin(request.user):
        return redirect('task_list')
    error = None
    if request.method == "POST":
        # Only admins can add tasks
        try:
            role = getattr(request.user.userprofile, 'role', None)
        except Exception:
            role = None
        # Final permission check before saving
        is_admin = user_is_admin(request.user)
        if not is_admin:
            return redirect('task_list')
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            # If this was an AJAX request, return JSON so client can update counts without reload
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'task': {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'start_time': str(task.start_time),
                    'end_time': str(task.end_time),
                    'retries': task.retries,
                }})
            return redirect('task_list')
        else:
            error = form.errors
            # Return the form with errors explicitly (status 200) so tests receive the form page
            empty_task = _EmptyTaskObj()
            return render(request, "main/task_form.html", {"form": form, "error": error, "action": "Add", "task": empty_task}, status=200)
    else:
        form = TaskForm()
    empty_task = _EmptyTaskObj()
    return render(request, "main/task_form.html", {"form": form, "error": error, "action": "Add", "task": empty_task})

@require_POST
@admin_required
@login_required
def ajax_cancel_task(request, task_id):
    from .models import Task
    task = get_object_or_404(Task, id=task_id)
    # Only allow admin to cancel
    if not user_is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
    task.status = 'cancelled'
    task.save()
    return JsonResponse({
        'success': True,
        'task_id': task.id,
        'new_status': task.status,
    })
