from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from natureself.django.otp import tools as otp_tools
from natureself.django.core import api
from natureself.django.core.validators import is_valid_email, is_valid_phone
from .utils import get_user_roles, serialize_user
from . import errors

LOGIN_TEMPLATE = getattr(settings, 'NS_LOGIN_TEMPLATE', 'account/login.html')
LOGOUT_TEMPLATE = getattr(settings, 'NS_LOGOUT_TEMPLATE', 'account/logout.html')
API_REGISTER_VIEW = getattr(settings, 'NS_REGISTER_VIEW', None)

User = get_user_model()

@require_http_methods(['POST'])
def api_login(request):
    """
    登录，网站前端、管理后台均使用该 API 登录。

    POST /api/account/login
    {
        // 登录凭证，直接传递给各个 Auth 后端，如何使用由 Auth 后端决定
        **credentials,

        // 可选参数，如果提供了，则只有指定角色的用户可以登录
        // 一般网站登录时无需此参数，管理后台登录时，需 role = "admin"
        "role": "superuser",
    }

    项目中启用了哪几个 Auth 后端，请在 settings.py 中找 AUTHENTICATION_BACKENDS，
    如果 AUTHENTICATION_BACKENDS 中没有配置的话，默认只有一个，即 ModelBackend。

    以下是几个 Backend 接受的 **credentails 参数：

    ModelBackend:
    * username（注意，cardpc 中通过 username 查找用户时，会搜索 username、phone、email）
    * password

    n.d.account.backends.SmsCodeBackend:
    * phone
    * code
    * identity: 如果没有提供 phone 参数，但是提供了 identity，则用 identity 作为 phone

    n.d.account.backends.EmailCodeBackend:
    * email
    * code
    * identity: 如果没有提供 email 参数，但是提供了 identity，则用 identity 作为 email

    简单的说，前端使用密码登录时，可以发送这样的请求：

    POST /api/account/login
    {
        username: xxx,
        password: xxx
    }

    使用邮箱或验证码登录时，可以发送这样的请求：

    POST /api/account/login
    {
        identity: xxx, // xxx 可以是邮箱或手机号，会自动检测
        code: xxx
    }

    如果登录时仅希望短信验证码、不希望尝试邮箱验证码，可以这样：

    POST /api/account/login
    {
        phone: xxx,
        code: xxx
    }
    """
    role = request.json.pop('role', None)

    user = authenticate(request, **request.json)
    if user is None:
        return api.bad_request(message='用户名或密码不正确')

    if role and role not in get_user_roles(user):
        return api.bad_request(message='用户名或密码不正确')

    login(request, user)
    return api.ok(message='登录成功', data=serialize_user(user))

@require_http_methods(['POST'])
@csrf_exempt
def api_logout(request):
    """登出 API

    POST /api/account/logout
    """
    logout(request)
    return api.ok(message='已登出')

@require_http_methods(['GET'])
@ensure_csrf_cookie
def api_get_info(request):
    """获取当前用户信息 API

    GET /api/account/info
    """
    if request.user.is_authenticated:
        return api.ok(data=serialize_user(request.user))
    else:
        return api.not_authorized(message='未登录')

@require_http_methods(['POST'])
def api_send_code(request):
    """发送验证码，此函数仅支持发送注册、短信登录、重置密码三种验证码

    POST /api/account/send-code
    {
        // 验证码用途，可以是：register, login, reset-password
        "usage": "register",

        // 有两种方式指定发送对象，
        // * 提供 phone 字段，则会发送短信， 提供 email 字段，则会发送邮件
        // * 提供 identity 字段，则会自动判断 identity 是手机号还是邮箱，从而执行相应的操作
        // phone、email、identity 三个参数只能提供一个
        "phone": "13912345678",
        "email": "zhangsan@example.com",
        "identity": "13912345678",
    }

    * 如果缺少参数（一般只在开发阶段），会返回 400，message 描述错误信息。
    * 如果传递的 phone、email 或 identity 非法，会返回 InvalidPhone, InvalidEmail 或 InvalidIdentity
    * 如果在静默期内重复请求，会返回 RateExceeded
    * 其他所有情况都会返回 200（比如被后端认定为恶意请求而没有发送，比如登录请求中提供的
      username 不存在而未发送等等），这些错误无需告知用户。

    登录、重置密码验证码，后端会查找用户，如果用户不存在，则不会发送验证码。
    如果用户存在，但是该用户的 phone_validated 为 False（即手机号未验证），
    也不会发送验证码。邮箱也是如此。即发送验证码的前置条件是相应的短信或邮箱已经验证过。

    对于注册验证码，我们不检查账号是否已经存在，也不会因为账号已存在而不发送短信。原因：
    * 如果我们告诉用户账号已存在，那么有心人可以遍历手机号来判断我们有哪些注册账号
    * 如果我们不告诉用户账号已存在、也不发送验证码，那么用户会很奇怪（用户收不到验证码，
      会觉得很奇怪）。让用户正常收验证码，在注册时会提示账号已存在。
    """
    usage = request.json.get('usage')
    if usage not in otp_tools.USAGES:
        return api.bad_request(message='Invalid "usage"')

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

    # 对于登录、重置密码的验证码，我们需要校验用户存在
    if usage in ['login', 'reset-password']:
        if phone:
            user = User.objects.filter(phone=phone, phone_validated=True).first()
        else:
            user = User.objects.filter(email=email, email_validated=True).first()

        if not user or not user.is_active:
            # 用户不存在或用户已锁定，不发送验证码，但仍然返回“验证码已发送”
            return api.ok(message='验证码已发送')

    recipient = phone or email
    engine = 'sms' if phone else 'email'
    vcode, result = otp_tools.generate_code(engine, request, recipient, usage=usage)
    if result == otp_tools.GENERATE_RESULTS.silent:
        return errors.RateExceeded()

    return api.ok(message='验证码已发送')

@require_http_methods(['POST'])
def api_verify_code(request):
    """检查验证码是否正确

    POST /api/account/verify-code
    {
        // 验证码用途，可以是：register, login, reset-password
        "usage": "register",

        // 与 send-code 类似，有两种方式指定发送对象
        // * 提供 phone 或 email 字段
        // * 提供 identity 字段
        "phone": "13912345678",
        "email": "zhangsan@example.com",
        "identity": "13912345678",

        // 用户输入的验证码
        "code": "123456",
    }

    如果成功，返回 200，否则返回 400。
    """
    usage = request.json.get('usage')
    if usage not in otp_tools.USAGES:
        return api.bad_request(message='Invalid "usage"')

    code = request.json.get('code')

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

    recipient = phone or email
    engine = 'sms' if phone else 'email'
    valid = otp_tools.verify_code(engine, request, recipient, usage, code, False)
    if valid:
        return api.ok(message='验证码正确')
    else:
        return errors.InvalidVerifyCode()

@require_http_methods(['POST'])
def api_reset_password(request):
    """修改密码 API

    支持使用旧密码来设置新密码，也支持使用验证码来设置新密码。

    在实现时，会将所有参数传递给 authenticate()，如果成功，则设置新密码。

    POST /api/account/reset-password
    {
        // 与登录 API 中的登录凭证一致
        **credentials,

        // 设置的新密码
        new_password: '123456',
    }
    """
    new_password = request.json.pop('new_password', None)
    if not new_password:
        return api.bad_request(message='Missing "new_password"')

    user = authenticate(request, **request.json, usage=otp_tools.USAGES.reset_password)
    if user:
        user.set_password(new_password)
        user.save()
        return api.ok(message='密码已更新')
    else:
        # TODO 应该给出更多的判断，从而给用户提供一些有效的报错信息
        # * 使用短信验证码重置密码时，如果手机号不存在，应该提示用户未注册
        #   注意，不应该在发送验证码时提示，而应该在发送之后再提示，避免信息泄漏。
        #   如果验证码错误应该提示验证码错误。
        # * 如果用户被锁定，可以提示用户被锁定
        # * 根据实际使用场景，提示旧密码错误/验证码错误等
        return api.bad_request(message='用户不存在或校验失败')


if API_REGISTER_VIEW:
    api_register = import_string(API_REGISTER_VIEW)
else:
    @require_http_methods(['POST'])
    def api_register(request):
        return api.not_implemented()

@require_http_methods(['GET'])
@ensure_csrf_cookie
def page_login(request):
    """登录页面
    """
    return render(request, LOGIN_TEMPLATE)

@require_http_methods(['GET'])
def page_logout(request):
    """登出页面
    """
    logout(request)
    return api.redirect(location='/')
