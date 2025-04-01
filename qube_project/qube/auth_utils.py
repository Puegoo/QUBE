from functools import wraps
from django.shortcuts import redirect
from .models import UserNode

def neo4j_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('username'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_current_user(request):
    username = request.session.get('username')
    if username:
        try:
            return UserNode.nodes.get(username=username)
        except UserNode.DoesNotExist:
            return None
    return None