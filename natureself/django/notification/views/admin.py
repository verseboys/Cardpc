from django import forms
from django.views import View
from django.utils.decorators import method_decorator
from email.utils import parseaddr

import re

from natureself.django.core import api
from natureself.django.core.utils import get_pagination, get_boolean_query, get_datetime_query
from natureself.django.account.decorators import role_required

from natureself.admin.forms import Form, panels
from natureself.admin.views import AdminView

from ..tools import send_mail
from ..models import Email, AliSms

@method_decorator(role_required(['admin']), name='dispatch')
class EmailView(AdminView):
    """
    API Endpoints for managing emails.

    GET /api/admin/notification/emails
        description: list (search) emails
        return: array of email objects, with pagination
        status: 200, 400
        query string:
            * subject: filter subject with 'icontains'
            * from: filter from_email with 'icontains'
            * recipient: filter recipients with 'icontains'
            * status: filter status with '='
            * sent_range: filter email sent between date, format: 2019-03-21,2019-03-22
            * pagination params (page=1, page_size=10)

    GET /api/admin/notification/emails/{id}
        description: get email model
        return: email object
        status: 200, 404

    POST /api/admin/notification/emails
        description: send email, supposed to be used as testing purpose only.
        return: email object on success
        status: 200, 400
        body:
            {
                subject: 'plain text',
                content: '',
                from: 'zhangsan@example.com',
                recipients: ['zhangsan@example.com', 'lisi@example.com'],
            }
    """
    MODEL = Email
    ORDER_BY = ['-sent_at']
    USE_PAGINATION = True

    CREATE_METHOD = 'create_email'
    UPDATE_METHOD = None
    PATCH_METHOD = None
    DELETE_METHOD = None

    SEARCH_FORM = Form([
        panels.TextPanel('recipients', form_field_name='recipient', search_op='icontains', label='收件人'),
        panels.TextPanel('from_email', form_field_name='from', search_op='icontains', label='发件人'),
        panels.TextPanel('subject', search_op='icontains', label='标题'),
        panels.SelectPanel('status', label='状态'),
        panels.DateRangePanel('sent_at', form_field_name='sent_range', label='发送日期'),
        ], model=MODEL, form_mode='search')

    def create_email(self, request):
        subject = request.json.get('subject')
        if not subject:
            return api.bad_request(form_errors=dict(subject=['标题不能为空']))

        content = request.json.get('content')
        if not content:
            return api.bad_request(form_errors=dict(content=['内容不能为空']))

        from_email = request.json.get('from_email')
        if not from_email:
            return api.bad_request(form_errors=dict(from_email=['发件人不能为空']))

        recipients = request.json.get('recipients')
        if not recipients:
            return api.bad_request(form_errors=dict(recipients=['收件人列表不能为空']))
        if not isinstance(recipients, list):
            return api.resopnse(400, form_errors=dict(recipients=['收件人列表必须是数组']))

        email = send_email(recipients, subject, from_email=from_email, content=content)

        return api.ok(data=email.serialize())

@method_decorator(role_required(['admin']), name='dispatch')
class AliSmsView(AdminView):
    """
    API Endpoints for managing ali sms.

    GET /api/admin/notification/alisms
        description: list (search) sms
        return: array of sms objects, with pagination
        status: 200, 400
        query string:
            * phone: filter phone_numbers with 'icontains'
            * content: filter content with 'icontains'
            * status: filter status with '='
            * sent_before: filter sms sent before the date, date format: '2019-03-21'
            * sent_after: filter sms sent after the date, date format: '2019-03-21'
            * pagination params (page=1, page_size=10)

    GET /api/admin/notification/alisms/{id}
        description: get sms model
        return: sms object
        status: 200, 404

    POST /api/admin/notification/alisms
        description: send sms, supposed to be used as testing purpose only.
        return: email object on success
        status: 200, 400
        body:
            {
                phone_numbers: '13912345678, 13812345678',
                signature_name: '大鱼测试',
                template_code: 'SMS_134310520',
                template_param: { code: '123456' },
            }
    """
    MODEL = AliSms
    ORDER_BY = ['-sent_at']
    USE_PAGINATION = True

    CREATE_METHOD = 'create_sms'
    UPDATE_METHOD = None
    PATCH_METHOD = None
    DELETE_METHOD = None

    SEARCH_FORM = Form([
        panels.TextPanel('phone_numbers', form_field_name='phone', search_op='icontains', labels='手机号'),
        panels.TextPanel('content', search_op='icontains', labels='内容'),
        panels.SelectPanel('status', labels='状态'),
        panels.DateRangePanel('sent_at', form_field_name='sent_range', label='发送日期'),
        ], model=MODEL, form_mode='search')

    def create_sms(self, request):
        phone_numbers = request.json.get('phone_numbers')
        if not phone_numbers:
            return api.bad_request(form_errors=dict(phone_numbers=['接收方手机号不能为空']))

        signature_name = request.json.get('signature_name')
        if not signature_name:
            return api.bad_request(form_errors=dict(signature_name=['签名不能为空']))
        if signature_name not in AliSms.SIGNATURES:
            return api.bad_request(form_errors=dict(signature_name=['不允许使用的签名']))

        template_code = request.json.get('template_code')
        if not template_code:
            return api.bad_request(form_errors=dict(template_code=['模板编号不能为空']))
        if template_code not in AliSms.TEMPLATES:
            return api.bad_request(form_errors=dict(template_code=['模板编号不存在']))

        template_param = reuqest.json.get('template_param', {})

        sms = send_sms(phone_numbers, signature_name, template_code, template_param)

        return api.ok(data=sms.serialize())
