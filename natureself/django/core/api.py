"""
Utils for building api server.
"""

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.paginator import Page as PaginatorPage
from django.db.models.query import QuerySet
from django.db.models import Model
from enum import IntEnum, unique

@unique
class Codes(IntEnum):
    OK = 0

    BAD_REQUEST = 400
    NOT_AUTHORIZED = 401
    PERMISSION_DENIED = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501

class Response(JsonResponse):
    def __init__(self, status=200, code=Codes.OK, message='', data=None, **kwargs):
        if isinstance(data, PaginatorPage) or isinstance(data, QuerySet):
            data = [item.serialize() for item in data]
        elif isinstance(data, Model):
            data = data.serialize()

        content = dict(code=code, message=message, data=data)
        if kwargs.get('pagination'):
            content['pagination'] = kwargs['pagination']
        if kwargs.get('event_id'):
            content['event_id']= kwargs['event_id']
        if kwargs.get('form_errors'):
            content['form_errors'] = kwargs['form_errors']
        if kwargs.get('login_url'):
            content['login_url'] = kwargs['login_url']
        super().__init__(data=content, status=status)

def ok(message='ok', code=Codes.OK, data=None, pagination=None):
    return Response(status=200, code=Codes.OK, message=message, data=data, pagination=pagination)

def created(message='resource created', data=None):
    return Response(status=201, code=Codes.OK, message=message, data=data)

def no_content():
    return HttpResponse(status=204)

def bad_request(message='bad request', code=Codes.BAD_REQUEST, form_errors=None, data=None):
    return Response(status=400, code=code, message=message, form_errors=form_errors, data=data)

def not_authorized(message='not authorized', login_url=None):
    return Response(status=401, code=Codes.NOT_AUTHORIZED, message=message, login_url=login_url)

def forbidden(message='forbidden'):
    return Response(status=403, code=Codes.PERMISSION_DENIED, message=message)

def not_found(message='not found'):
    return Response(status=404, code=Codes.NOT_FOUND, message=message)

def invalid_endpoint(message='invalid endpoint'):
    return Response(status=404, code=Codes.NOT_FOUND, message=message)

def method_not_allowed(message='method not allowed'):
    return Response(status=405, code=Codes.METHOD_NOT_ALLOWED, message=message)

def internal_server_error(message='internal server error', event_id=None):
    return Response(status=500, code=Codes.INTERNAL_SERVER_ERROR, message=message, event_id=event_id)

def not_implemented(message='not implemented'):
    return Response(status=501, code=Codes.NOT_IMPLEMENTED, message=message)

def redirect(location, permanent=False):
    if permanent:
        return HttpResponsePermanentRedirect(location)
    else:
        return HttpResponseRedirect(location)

def define_application_error(code, message_template):
    class ApplicationError(Response):
        def __init__(self, data=None):
            data = {} if data is None else data
            super().__init__(status=Codes.BAD_REQUEST, code=code, message=message_template.format(data))
    return ApplicationError
