from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        # Allow superusers or users with UserProfile.role == 'admin'
        if not user.is_authenticated:
            return redirect('login')
        try:
            if user.is_superuser or getattr(user.userprofile, 'role', '') == 'admin':
                return view_func(request, *args, **kwargs)
        except Exception:
            pass
        # Redirect non-admin users to the task list to match previous behavior
        return redirect('task_list')
    return _wrapped
