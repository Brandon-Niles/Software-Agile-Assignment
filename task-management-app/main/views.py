from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import random

task_names = [
    "Database Backup", "Firewall Rule Update", "User Account Provisioning", "Patch Deployment",
    "Web Server Restart", "Antivirus Scan", "Log Rotation", "Disk Space Monitoring",
    "SSL Certificate Renewal", "Network Latency Test", "Load Balancer Config", "API Health Check",
    "Data Sync", "Cache Clear", "System Reboot", "Security Audit", "Email Queue Flush",
    "DNS Propagation", "Container Deployment", "Service Scaling"
]

locations_list = [
    "Frankfurt, Germany", "London, UK", "Mumbai, India", "Tokyo, Japan", "New York, USA",
    "Paris, France", "Sydney, Australia", "Singapore", "Dublin, Ireland", "San Francisco, USA"
]

platforms_list = ["AWS", "Azure", "GCP", "On-prem"]
statuses = ["Running", "Pending", "Completed", "Failed"]

# Generate tasks with random dates between 2024 2025
start_range = datetime(2024, 1, 1, 0, 0)
end_range = datetime(2025, 12, 31, 23, 59)
delta = end_range - start_range

TASKS = []
for i in range(1, 101):
    name = random.choice(task_names)
    location = random.choice(locations_list)
    platform = random.choice(platforms_list)
    status = random.choice(statuses)
    # Random date within the range
    random_minutes = random.randint(0, int(delta.total_seconds() // 60))
    start_time_dt = start_range + timedelta(minutes=random_minutes)
    start_time = start_time_dt.strftime("%Y-%m-%d %H:%M")
    end_time = "" if status in ["Running", "Pending"] else (start_time_dt + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")
    retries = random.randint(0, 3)
    TASKS.append({
        "id": i,
        "name": name,
        "location": location,
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "platform": platform,
        "retries": retries
    })

@login_required
def task_list(request):
    search = request.GET.get('search', '').strip().lower()
    platform = request.GET.get('platform', '')
    location = request.GET.get('location', '')
    date = request.GET.get('date', '')

    filtered = TASKS
    if search:
        filtered = [t for t in filtered if search in t["name"].lower() or search in str(t["id"])]
    if platform:
        filtered = [t for t in filtered if t["platform"] == platform]
    if location:
        filtered = [t for t in filtered if t["location"] == location]
    if date:
        filtered = [t for t in filtered if t["start_time"].startswith(date)]

    platforms = sorted(set(t["platform"] for t in TASKS))
    locations = sorted(set(t["location"] for t in TASKS))

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

def login_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
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
