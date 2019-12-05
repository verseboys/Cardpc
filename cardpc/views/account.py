from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db import IntegrityError

from natureself.django.core.shortcuts import render_for_ua
from natureself.django.core.validators import is_valid_email, is_valid_phone
from natureself.django.account import errors
from natureself.django.account.utils import serialize_user
from natureself.django.otp import tools as otp_tools
from natureself.django.core import api

from cardpc.models import User

"""
登录、注册、重置密码使用同一个 HTML 页面。
"""

@require_http_methods(['GET'])
@ensure_csrf_cookie
def page_login(request):
    """
    登录页面

    GET /account/login/
    """
    return render_for_ua(request, 'cardpc/account/index.html', context=dict(app='login'))

@require_http_methods(['GET'])
@ensure_csrf_cookie
def page_register(request):
    """
    注册页面

    GET /account/register/
    """
    return render_for_ua(request, 'cardpc/account/index.html', context=dict(app='register'))

@require_http_methods(['GET'])
@ensure_csrf_cookie
def page_reset_password(request):
    """
    重置密码页面

    GET /account/reset-password/
    """
    return render_for_ua(request, 'cardpc/account/index.html', context=dict(app='reset-password'))

@require_http_methods(['POST'])
def api_register(request):
    """
    注册 API

    POST /api/account/register
    {
        // 与登录 API 类似，可以明确指定 phone+code 或 email+code 或 identity+code
        "identity": "13912345678",
        "code": "123456",

        "phone": "13912345678",
        "code": "123456",

        "email": "zhangsan@example.com",
        "code": "123456",

        "password": "123456",
    }
    """
    code = request.json.get('code')
    if not code:
        return errors.InvalidVerifyCode()

    password = request.json.get('password')
    if not password:
        return api.bad_request('Missing "password"')

    identity = request.json.get('identity')
    phone = request.json.get('phone')
    email = request.json.get('email')

    if phone:
        if not is_valid_phone(phone):
            return errors.InvalidPhone()
    elif email:
        if not is_valid_email(email):
            return errors.InvalidEmail()
    elif identity:
        if is_valid_phone(identity):
            phone = identity
        elif is_valid_email(identity):
            email = identity
        else:
            return errors.InvalidIdentity()
    else:
        return api.bad_request(message='Missing "phone", "email" or "identity"')

    if phone:
        find_user_args = dict(phone=phone, phone_validated=True)
        create_user_args = dict(phone=phone, phone_validated=True, password=password)
        vcode_engine = 'sms'
        recipient = phone
    else:
        create_user_args = dict(email=email, email_validated=True, password=password)
        vcode_engine = 'email'
        recipient = email

    valid = otp_tools.verify_code(vcode_engine, request, recipient, 'register', code, True)
    if not valid:
        return errors.InvalidVerifyCode()

    # 由于数据库中不宜为 phone、email 添加 unique contraint
    # （主要是 Django 里的实现，如果要添加 unique contraint，那么 phone、email
    # 比如允许为 null，但 django 中 email 并未声明允许为 null，一些地方的代码
    # 也有这样的假定，因此我们尽量不打破这种惯例）
    # 我们手动判断邮箱或手机号是否存在，如果存在则报错。这会存在 race condition，
    # 有可能两个并发的请求导致创建了邮箱或手机号相同的账号，不过这种概率应该很低。
    # 除非两个请求同时运行上述 verify_code 并且都返回了 True （极小概率时间），
    # 而且这里又同时读取数据库、创建新用户，才会导致问题。因此暂时不考虑这个问题。

    if phone:
        if User.objects.filter(phone=phone, phone_validated=True).exists():
            return errors.PhoneExists()
        user = User.objects.create_user(phone=phone, phone_validated=True, password=password)
    else:
        if User.objects.filter(email=email, email_validated=True).exists():
            return errors.EmailExists()
        user = User.objects.create_user(email=email, email_validated=True, password=password)

    return api.ok(data=serialize_user(user))
