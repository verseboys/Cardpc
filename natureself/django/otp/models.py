from django.db import models
from django.conf import settings
from django.utils import timezone
from natureself.django.notification.tools import send_sms, send_mail

import random
import jsonfield
from model_utils import Choices

class VerifyCodeManager(models.Manager):
    def create(self, request, recipient, usage, silent_duration=None, valid_duration=None, clone=None):
        silent_duration = silent_duration or self.model.DEFAULT_SILENT_DURATION
        valid_duration = valid_duration or self.model.DEFAULT_VALID_DURATION
        now = timezone.now()

        if clone:
            code = clone.code
        else:
            code = ''.join(random.choices('0123456789', k=6))

        message = self.model.send_message(recipient, usage, code)

        return super().create(
                message = message,
                recipient = recipient,
                code = code,
                generated_at = now,
                silent_before = now + timezone.timedelta(seconds=silent_duration),
                expires_at = now + timezone.timedelta(seconds=valid_duration),
                session_key = request.session.session_key,
                verify_count = 0,
                used = False,
                client_meta = dict(
                    client_ip = request.META['REMOTE_ADDR'],
                    user_agent = request.META.get('HTTP_USER_AGENT', ''),
                    ),
                clone = clone,
                usage = usage,
                )

    def filter_valid(self):
        return self.filter(expires_at__gt=timezone.now()) \
                   .filter(verify_count__lt=self.model.VERIFY_COUNT_LIMIT) \
                   .filter(used=False)

class VerifyCode(models.Model):
    """
    短信/邮件验证码，每一个 VerifyCode 对应一条真实发送的信息。
    这是虚拟基类，请使用 SmsVerifyCode 或 EmailVerifyCode
    """
    class Meta:
        abstract = True

    objects = VerifyCodeManager()

    # 默认的有效时间长度（每一个验证码在创建时允许单独提供有效期，但不鼓励单独设置）
    DEFAULT_VALID_DURATION = 600
    # 在发送验证码后，多久之后才可以发送下一次
    DEFAULT_SILENT_DURATION = 60
    # 一个验证码可以被校验几次
    VERIFY_COUNT_LIMIT = 5

    # 接收验证码的手机号或邮箱
    recipient = models.TextField(blank=False)
    # 生成的验证码（一经生成，禁止修改）
    code = models.TextField()
    # 生成时间（一经生成，禁止修改）
    generated_at = models.DateTimeField()
    # 在该时间前，不生成新的Code、发送新的短信
    silent_before = models.DateTimeField()
    # 有效期时间（一经生成，禁止修改）
    expires_at = models.DateTimeField()
    # 该 code 在某个 session 下生成的，则只能在相应的 session 下使用（一经生成，禁止修改）
    session_key = models.TextField(blank=False)
    # 校验请求的次数
    verify_count = models.IntegerField(default=0)
    # 是否已经使用过，一经使用立即失效
    used = models.BooleanField(default=False)
    # 客户端信息，如 IP 地址、UserAgent 等
    client_meta = jsonfield.JSONField(default=dict)
    # 如果一个验证码是从另一个复制过来的，clone 指向其复制源
    clone = models.ForeignKey('self', models.SET_NULL, null=True)

    USAGES = Choices(
            ('login', 'login', '登录验证码'),
            ('register', 'register', '注册验证码'),
            ('reset-password', 'reset_password', '重置密码'),
            )
    usage = models.TextField(choices=USAGES)

    def is_valid(self):
        return (self.expires_at > timezone.now()) \
                and (self.verify_count < self.VERIFY_COUNT_LIMIT) \
                and (not self.used)

    def inc_verify_count(self, save=True):
        self.verify_count = models.F('verify_count') + 1
        if save:
            self.save(update_fields=['verify_count'])

    def mark_used(self, save=True):
        self.used = True
        if save:
            self.save(update_fields=['used'])

        if self.clone:
            self.clone.mark_used(save)

class SmsVerifyCode(VerifyCode):
    message = models.ForeignKey('notification.AliSms', models.CASCADE)

    SIGNATURE = settings.NS_OTP_ALI_SMS_SIGNATURE
    TEMPLATES = {
            'login': settings.NS_OTP_ALI_SMS_LOGIN_TEMPLATE,
            'register': settings.NS_OTP_ALI_SMS_REGISTER_TEMPLATE,
            'reset-password': settings.NS_OTP_ALI_SMS_RESET_PASSWORD_TEMPLATE,
            }
    DEFAULT_TEMPLATE_PARAM = settings.NS_OTP_ALI_SMS_DEFAULT_TEMPLATE_PARAM

    @classmethod
    def send_message(cls, recipient, usage, code):
        return send_sms(
                phone_numbers = recipient,
                signature_name = cls.SIGNATURE,
                template_code = cls.TEMPLATES[usage],
                template_param = dict(code=code, **cls.DEFAULT_TEMPLATE_PARAM),
                )

class EmailVerifyCode(VerifyCode):
    message = models.ForeignKey('notification.Email', models.CASCADE)

    FROM = settings.NS_OTP_EMAIL_FROM
    TITLE = settings.NS_OTP_EMAIL_TITLE
    TEMPLATES = {
            'login': settings.NS_OTP_EMAIL_LOGIN_TEMPLATE,
            'register': settings.NS_OTP_EMAIL_REGISTER_TEMPLATE,
            'reset-password': settings.NS_OTP_EMAIL_RESET_PASSWORD_TEMPLATE,
            }
    DEFAULT_TEMPLATE_CONTEXT = settings.NS_OTP_EMAIL_DEFAULT_TEMPLATE_CONTEXT

    @classmethod
    def send_message(cls, recipient, usage, code):
        return send_mail(
                recipient,
                cls.TITLE,
                from_email = cls.FROM,
                template = cls.TEMPLATES[usage],
                context = dict(code=code, **cls.DEFAULT_TEMPLATE_CONTEXT),
                )
