from . import api

def error_400(request, exception, template_name='400.html'):
    return api.bad_request()

def error_403(request, exception, template_name='403.html'):
    return api.forbidden()

def error_404(request, exception, template_name='404.html'):
    return api.not_found()

def error_500(request, template_name='500.html'):
    event_id = hasattr(request, 'sentry') and request.sentry['id'] or None
    return api.internal_server_error(event_id=event_id)
