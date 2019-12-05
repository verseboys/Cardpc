from django.db import models
from django.conf import settings
from django.utils import timezone

import re
import json
from model_utils import Choices
import jsonfield
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

import logging
logger = logging.getLogger(__name__)

DRYRUN = getattr(settings, 'ALI_SMS_DRY_RUN', False)
# 以下为必须的配置字段，如果用户没有配置，这里会直接抛出 AttributeError，终止进程启动
ALI_SMS_ACCESS_KEY_ID = settings.ALI_SMS_ACCESS_KEY_ID
ALI_SMS_ACCESS_KEY_SECRET = settings.ALI_SMS_ACCESS_KEY_SECRET

def send_sms(phone_numbers, signature_name, template_code, template_param):
    return AliSms.objects.send_sms(phone_numbers, signature_name, template_code, template_param)

def _alisdk_send_sms(phone_numbers, signature_name, template_code, template_param):
    client = AcsClient(ALI_SMS_ACCESS_KEY_ID, ALI_SMS_ACCESS_KEY_SECRET, 'default')

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    request.add_query_param('PhoneNumbers', phone_numbers)
    request.add_query_param('SignName', signature_name)
    request.add_query_param('TemplateCode', template_code)
    if not isinstance(template_param, str):
        template_param = json.dumps(template_param)
    request.add_query_param('TemplateParam', template_param)
    response = client.do_action(request)

    return json.loads(response)

class AliSmsManager(models.Manager):
    def send_sms(self, phone_numbers, signature_name, template_code, template_param):
        # clean data
        # removes spaces in between commas
        phone_numbers = ','.join([n.strip() for n in phone_numbers.split(',')])

        # check if signature exists
        if signature_name not in self.model.SIGNATURES:
            raise ValueError(f'Invalid signature_name: {signature_name}')

        # check template:
        #    template_code should exist
        #    all template_param values should be str type
        #    template_param should cover all variables in template
        # also send template_param with only required params
        if template_code not in self.model.TEMPLATES:
            raise ValueError(f'Invalid template_code: {template_code}')
        template = self.model.TEMPLATES[template_code]
        for key, val in template_param.items():
            if not isinstance(val, str):
                raise ValueError(f'template_param[{key}] is not str: {val}')
        new_template_params = {}
        for var in self.model.TEMPLATE_VARIABLE_PATTERN.findall(template):
            if var not in template_param:
                raise ValueError(f'Missing template variable in template_param: {var}')
            else:
                new_template_params[var] = template_param[var]
        template_param = new_template_params

        # render template to message for archive
        content = self.model.TEMPLATE_VARIABLE_PATTERN.sub(lambda p: template_param[p.group('key')], template)

        # create and save the model
        sms = self.model(
                phone_numbers = phone_numbers,
                signature_name = signature_name,
                template_code = template_code,
                template_param = template_param,
                access_key_id = ALI_SMS_ACCESS_KEY_ID,
                content = f'【{signature_name}】{content}',
                )
        sms.save()

        if DRYRUN:
            logging.info(f'to: {sms.phone_numbers}, content: {sms.content}')
            sms.sent_at = timezone.now()
            sms.status = self.model.STATUSES.dryrun
            sms.save()

            return sms

        # 发送短信
        # 将来需要实现异步发送
        # TODO 需要实现频率控制，包括单 IP 限制、单手机号限制、总频率限制、其他风控措施（例如需要验证码才能发送短信等）
        response = _alisdk_send_sms(phone_numbers, signature_name, template_code, template_param)
        sms.sent_at = timezone.now()
        # 见 https://sentry.evahealth.net/ns/cardpc/issues/751/
        # 在发生错误时，可能没有 BizId，消息样例：
        # {
        #   'Code': 'isv.BUSINESS_LIMIT_CONTROL',
        #   'Message': '触发小时级流控Permits:5',
        #   'RequestId': '6E3636E5-2708-4DFD-B2A2-923A47B6EA0F'
        # }
        sms.ali_bizid = response.get('BizId', '')
        sms.ali_code = response['Code']
        sms.ali_message = response['Message']
        if response['Code'] == 'OK':
            sms.status = self.model.STATUSES.success
        else:
            sms.status = self.model.STATUSES.failed
        sms.save()

        return sms

class AliSms(models.Model):
    """
    使用阿里云短信服务发送的短信记录
    """

    objects = AliSmsManager()

    # 短信签名，需在阿里云控制台配置。当阿里云控制台上变更设置时，这里也需要变更
    SIGNATURES = Choices(
            ('泽创天成', 'zechuang', '泽创天成'),
            ('医维云', 'einmatrix', '医维云'),
            ('医维云科研大数据平台', 'edc', '医维云科研大数据平台'),
            ('基层呼吸联盟', 'cardpc-old', '中国基层呼吸防治联盟'),
            ('中国基层呼吸疾病防治联盟', 'cardpc', '中国基层呼吸疾病防治联盟'),
            # 以下为赠送签名，可能会失效
            ('大鱼测试', 'dayuceshi', '大鱼测试'),
            ('活动验证', 'huodongyanzheng', '活动验证'),
            ('变更验证', 'biangengyanzheng', '变更验证'),
            ('登录验证', 'dengluyanzheng', '登录验证'),
            ('注册验证', 'zhuceyanzheng', '注册验证'),
            ('身份验证', 'shenfenyanzheng', '身份验证'),
            )

    # 短信模板，需在阿里云控制台配置。当阿里云控制台上变更设置时，这里也需要变更
    TEMPLATES = Choices(
            ('SMS_134310520', 'einmatrix', '您的验证码为 ${code}，此验证码用于您的手机验证。10分钟内有效。'),
            ('SMS_133972398', 'login', '您的验证码：${code}，您正进行身份验证，该验证码5分钟内有效，打死不告诉别人！'),
            ('SMS_66610220', 'shenfenyanzheng', '验证码${code}，您正在进行${product}身份验证，打死不要告诉别人哦！'),
            ('SMS_66610219', 'duanxinceshi', '尊敬的${customer}，欢迎您使用阿里云通信服务！'),
            ('SMS_66610218', 'dengluqueren', '验证码${code}，您正在登录${product}，若非本人操作，请勿泄露。'),
            ('SMS_66610217', 'dengluyichang', '验证码${code}，您正尝试异地登录${product}，若非本人操作，请勿泄露。'),
            ('SMS_66610216', 'yonghuzhuce', '验证码${code}，您正在注册成为${product}用户，感谢您的支持！'),
            ('SMS_66610215', 'huodongqueren', '验证码${code}，您正在参加${product}的${item}活动，请确认系本人申请。'),
            ('SMS_66610214', 'xiugaimima', '验证码${code}，您正在尝试修改${product}登录密码，请妥善保管账户信息。'),
            ('SMS_66610213', 'xinxibiangeng', '验证码${code}，您正在尝试变更${product}重要信息，请妥善保管账户信息。'),
            ('SMS_162524735', 'edc_visit_notification', '您好，${study}的受试者编号为${case_id}的${event_name}访视${visit_status}，请登录平台查看详情，及时开展访视！'),
            ('SMS_164800307', 'verifycode', '验证码为：${code}，10分钟内有效，若非本人操作请忽略，请勿泄漏验证码。'),
            )
    # 模版中变量的匹配 pattern
    TEMPLATE_VARIABLE_PATTERN = re.compile(r'\${(?P<key>[^}]+)}')

    # 短信发送状态
    # 目前我们使用同步发送的方式，即调用 send_sms() 会立即发送，在发送之后才会返回，
    # 但是将来我们可能会采用异步发送的方式，即 send_sms() 仅仅将短信加入待发送队列，然后异步调度发送，
    # 从而可以实现频率限制等功能。
    STATUSES = Choices(
        # pending 表示已经将短信加入待发送队列，等待被发送，限制使用同步发送的方式，短信不会处于该状态
        ('pending', 'pending', '待发送'),
        # reject 表示由于某种原因拒绝发送，例如超过发送频率限制，或其他内部限制。目前没有实现这方面限制，所以不会处于该状态
        ('reject', 'reject', '拒绝发送'),
        # 表示已经调用了第三方服务商的 SDK，但是有些第三方可能需要异步检查发送结果，
        # 我们获得这个结果前处于该状态。目前阿里大鱼服务会立刻返回结果，所以目前不会处于该状态
        ('sent', 'sent', '已发送'),
        # 表示短信已经发送成功（服务商没有返回错误）（但这并不代表短信一定发送成功）。
        ('success', 'success', '发送成功'),
        # 表示在发送短信时，服务商返回了错误
        ('failed', 'failed', '发送失败'),
        # 表示这条短信仅仅是本地测试使用，没有真实发送出去
        ('dryrun', 'dryrun', '本地测试'),
    )

    # 阿里云：手机号，11位手机号码，支持对多个手机号码发送短信，手机号码之间以英文逗号（,）分隔。
    # 我们不建议使用批量发送，应当总是单独发送
    phone_numbers = models.TextField()
    # 阿里云：短信签名名称。请在控制台签名管理页面签名名称一列查看。
    signature_name = models.TextField(choices=SIGNATURES)
    # 阿里云：短信模板ID。请在控制台模板管理页面模板CODE一列查看。
    template_code = models.TextField(choices=TEMPLATES)
    # 阿里云：短信模板变量对应的实际值，JSON格式。
    # 注：由于我们本地测试时可能会使用 sqlite，因此这里不使用 postgres 的 jsonb。
    # 我们这里不需要在数据库中查询 template_param，因此不用考虑性能的问题
    template_param = jsonfield.JSONField(default=dict)
    # 阿里云 access id。考虑到测试环境、生产环境可能使用不同的 access key，查询短信状态时需要使用相同的 key
    access_key_id = models.TextField()
    # 渲染后的短信内容，这个内容在本地渲染，仅作存档使用
    content = models.TextField()

    # 以下为阿里云SDK回复的内容，这些字段在调用阿里云 SDK 之后再显示
    # 阿里云：发送回执ID，可根据该ID在接口QuerySendDetails中查询具体的发送状态。
    ali_bizid = models.TextField()
    # 阿里云：请求状态码。返回OK代表请求成功。其他错误码详见错误码列表。
    # https://help.aliyun.com/document_detail/101346.html?spm=a2c4g.11186623.2.14.b4b856e0DbzXik
    ali_code = models.TextField()
    # 状态码的描述。
    ali_message = models.TextField()

    # 短信发送状态
    status = models.TextField(choices=STATUSES)

    # 调用 send_sms() 的时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 实际调用阿里云 SDK 的时间
    sent_at = models.DateTimeField(null=True)

    def __str__(self):
        return f'to: {self.phone_numbers}, message: {self.content}'

    def serialize(self, to_dict=True):
        data = dict(
                phone_numbers = [n.strip() for n in self.phone_numbers.split(',')],
                content = self.content,
                status = self.status,
                created_at = self.created_at,
                sent_at = self.sent_at,
                ali_bizid = self.ali_bizid,
                ali_code = self.ali_code,
                ali_message = self.ali_message,
                )

        return data if to_dict else json.dumps(data, ensure_ascii=False)
