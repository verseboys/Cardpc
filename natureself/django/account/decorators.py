from functools import wraps
from natureself.django.core import api
from .utils import get_user_roles

def role_required(roles, response_func=None):
    if not response_func:
        response_func = api.forbidden

    def wrapper(viewfunc):
        @wraps(viewfunc)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return response_func()
            user_roles = get_user_roles(request.user)
            if any([(role in roles) for role in user_roles]):
                return viewfunc(request, *args, **kwargs)
            else:
                return response_func()
        return _wrapped_view
    return wrapper
