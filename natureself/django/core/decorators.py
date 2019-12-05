from functools import wraps
from . import api

def private_network_required(viewfunc):
    """
    只允许内网访问，一般用于管理后台的 API。注意，这个装饰器依赖 VisitorLocationMiddleware 这个中间件才能工作。
    """
    @wraps(viewfunc)
    def _wrapped_view(request, *args, **kwargs):
        if request.visitor_location == 'private':
            return viewfunc(request, *args, **kwargs)
        else:
            return api.forbidden()
    return _wrapped_view
