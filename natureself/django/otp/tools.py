from django.db.models import Q
from django.utils import timezone
from natureself.django.core.validators import is_valid_email, is_valid_phone

from model_utils import Choices

from .models import VerifyCode, SmsVerifyCode, EmailVerifyCode

USAGES = VerifyCode.USAGES

GENERATE_RESULTS = Choices(
    # 一切正常，生成了验证码
    ('ok', 'ok', '已发送验证码'),
    # 接收的手机号或邮箱非法
    ('invalid_recipient', 'invalid_recipient', '接收的手机号或邮箱无效'),
    # 在最近的静默期（默认一分钟）内
    ('silent', 'silent', '请求太频繁，未发送验证码'),
)

def validate_recipient(engine, recipient):
    if engine == 'sms' and is_valid_phone(recipient):
        return True
    if engine == 'email' and is_valid_email(recipient):
        return True
    return False

def generate_code(engine, request, recipient, usage, silent_duration=None, valid_duration=None):
    """
    生成验证码，返回 (verify_code, generate_result)

    engine: sms 或 email
    request: 当前请求的 request 对象
    recipient: 手机号或邮箱
    usage: Choices，见 USAGES，目前有 login 和 register
    silent_duration: 在此后多长时间内不再发送新的验证码，默认为60秒
    """
    if engine == 'email':
        VCode = EmailVerifyCode
    elif engine == 'sms':
        VCode = SmsVerifyCode
    else:
        raise ValueError('Invalid "engine", choices are: sms, email')

    if usage not in VCode.USAGES:
        raise ValueError(f'Invalid "usage", choices are: {",".join([u[0] for u in VCode.USAGES])}')

    if not validate_recipient(engine, recipient):
        return None, GENERATE_RESULTS.invalid_recipient

    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    now = timezone.now()

    # 查找当前是否在静默期，即相应的手机号或邮箱，是否存在还未到 silent_before 的记录
    # 如果在静默期，则取出有效期最新的一个验证码
    # * 如果该验证码仍有效（在有效期内、且未被标记为失效），则返回该验证码
    # * 如果验证码有效，但手机号不同、或 session 不同，则返回 None
    # * 如果该验证码已失效，则返回 None
    try:
        vcode = VCode.objects \
                .filter(Q(recipient=recipient) | Q(session_key=session_key)) \
                .filter(silent_before__gt=now) \
                .latest('expires_at')

        if not vcode.is_valid():
            return None, GENERATE_RESULTS.silent

        if vcode.recipient != recipient or vcode.session_key != session_key:
            return None, GENERATE_RESULTS.silent

        return vcode, GENERATE_RESULTS.silent
    except VCode.DoesNotExist:
        pass

    # 当前不在静默期，因此允许生成新的校验码并发送消息
    # 我们首先查找是否存在有效的验证码，判断条件为：
    # * usage 相同
    # * recipient、session_key都相同
    # * 在有效期内，
    # * 未超过校验次数限制
    # * 未被成功校验过
    # * 符合上述条件的可能有多个，只选择失效期最新的一个（即旧的自动认为失效）
    # 根据查找结果处理
    # * 如果存在，则使用相同的 code 生成新的消息
    # * 如果不存在，则生成新的 code 并生成新的消息
    try:
        vcode = VCode.objects \
                .filter_valid() \
                .filter(usage=usage) \
                .filter(recipient=recipient, session_key=session_key) \
                .latest('expires_at')

        new = VCode.objects.create(request, recipient, usage, silent_duration=silent_duration, valid_duration=valid_duration, clone=vcode)
        return new, GENERATE_RESULTS.ok
    except VCode.DoesNotExist:
        pass

    # 生成新的 code，并发送信息
    vcode = VCode.objects.create(request, recipient, usage, silent_duration=silent_duration, valid_duration=valid_duration)
    return vcode, GENERATE_RESULTS.ok

def verify_code(engine, request, recipient, usage, code, mark_used_on_success=True):
    """
    校验验证码是否正确，返回 True/False

    mark_used_on_success: 当校验成功后，是否标记为已经使用。在注册验证码的场景中，
    第一次校验时无需标记已使用，正式的注册请求中才需要标记为已使用。
    """
    if engine == 'email':
        VCode = EmailVerifyCode
    elif engine == 'sms':
        VCode = SmsVerifyCode
    else:
        raise ValueError('Invalid "engine", choices are: sms, email')

    if usage not in VCode.USAGES:
        raise ValueError(f'Invalid "usage", choices are: {",".join([u[0] for u in VCode.USAGES])}')

    if not code:
        return False

    # 用户没有 session，直接返回 False
    if not request.session.session_key:
        return False

    now = timezone.now()

    # 查询出仍有效的验证码，判断条件为：
    # * usage 相同
    # * recipient、session_key 均相同
    # * 在有效期内
    # * 未超过校验次数限制
    # * 未被成功校验过
    # * 符合上述条件的可能有多个，只选择失效期最新的一个（即旧的自动认为失效）
    # 根据查找结果处理：
    # * 如果不存在，返回 False
    # * 如果存在:
    #   * 如果 code 相同，校验成功，标记已使用，返回 True
    #   * 如果 code 不同，增加校验次数，返回 False
    # NOTE：校验次数限制是为了方式用户通过暴力枚举的方式找到正确的验证码，
    # 在上述逻辑中，以下请看不会增加校验计数，是没有问题但
    # * 校验成功不增加校验次数
    # * 已经失效的验证码不增加校验计数，
    # * 对于一定会返回失败的操作不增加校验计数
    try:
        vcode = VCode.objects \
                .filter_valid() \
                .filter(usage=usage) \
                .filter(recipient=recipient, session_key=request.session.session_key) \
                .latest('expires_at')
    except VCode.DoesNotExist:
        return False

    if vcode.code != code:
        vcode.inc_verify_count(save=True)
        return False

    # 校验成功，标记已使用，保存 session，返回 True
    if mark_used_on_success:
        vcode.mark_used(save=True)

    return True
