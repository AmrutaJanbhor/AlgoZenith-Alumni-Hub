from functools import wraps
from django.shortcuts import redirect

def approval_required(view_func):
    """Decorator to restrict access to approved users."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_approved:
            return redirect('approval_pending')  # Make sure this URL exists in urls.py
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view