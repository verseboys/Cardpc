#SECRET_KEY = 'nc=g3&7b2$u_y&64z$r-k=6ivk+0n#_vp&ado6-zv553l5@(k8'

# 在 DEBUG=True 的情况下不会启用 RAVEN，本地开发时 DEBUG 默认为 True，因此这里无需配置 RAVEN_CONFIG，
# 但在生产环境部署时，必须提供该配置。
## sentry config
# ref: https://docs.sentry.io/clients/python/integrations/django/
## for ssl to work, see: https://community.letsencrypt.org/t/problems-with-sentry-and-letsencrypt/19948/3
#RAVEN_CONFIG = {
#    'dsn': 'https://xxx:sentry.evahealth.net/x',
#    'transport': 'raven.transport.threaded_requests.ThreadedRequestsHTTPTransport',
#}

DATABASES = {
    # 本地开发时使用 sqlite
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
    # 如果要使用 dbfarm，请将上面一段代码注释掉，并使用下面这一段配置，根据数据库的信息补全配置
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'HOST': '',
    #     'PORT': '5432',
    #     'NAME': '',
    #     'USER': '',
    #     'PASSWORD': '',
    # },
}

# 阿里云短信配置，用于 natureself.django.notification
# 当 DRY_RUN 为 True 时，不会实际发送短信，而是会将短信内容打印到终端，在本地开发环境中使用
ALI_SMS_DRY_RUN = True
ALI_SMS_ACCESS_KEY_ID = '****************'
ALI_SMS_ACCESS_KEY_SECRET = '******************************'

# 邮件配置，用于 natureself.django.notification
# 当 DRY_RUN 为 True 时，不会实际发送邮件，而是会讲邮件打印到终端，在本地开发环境中使用
EMAIL_DRY_RUN = True
# 在内网测试时，可以使用 smtp.natureself.site，生产环境由运维进行配置
EMAIL_HOST = 'smtp.natureself.site'
EMAIL_PORT = '25'
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''
#EMAIL_USE_TLS = True

ZHIXIANG = dict(
    training = dict(
        investigation_wjx_url_pattern = 'https://natureself.wjx.cn/jq/39121051.aspx?sojumpparm=%s',
        qualification_wjx_url_pattern = 'https://www.wjx.top/jq/39121467.aspx?sojumpparm=%s',
    ),
)

NS_OTP_ALI_SMS_SIGNATURE = '中国基层呼吸疾病防治联盟'
NS_OTP_ALI_SMS_REGISTER_TEMPLATE = 'SMS_164800307'
NS_OTP_ALI_SMS_RESET_PASSWORD_TEMPLATE = 'SMS_164800307'
NS_OTP_ALI_SMS_LOGIN_TEMPLATE = 'SMS_164800307'
NS_OTP_ALI_SMS_DEFAULT_TEMPLATE_PARAM = {}

NS_OTP_EMAIL_FROM = '中国基层呼吸疾病防治联盟 <noreply@m.cardpc.org>'
NS_OTP_EMAIL_TITLE = '中国基层呼吸疾病防治联盟'
NS_OTP_EMAIL_REGISTER_TEMPLATE = 'cardpc/emails/register-code.html'
NS_OTP_EMAIL_RESET_PASSWORD_TEMPLATE = 'cardpc/emails/reset-password-code.html'
NS_OTP_EMAIL_LOGIN_TEMPLATE = 'cardpc/emails/login-code.html'
NS_OTP_EMAIL_DEFAULT_TEMPLATE_CONTEXT = {}

POLYV = dict(
    SECRETKEY = '..........',
)
