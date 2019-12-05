from natureself.django.core.api import define_application_error

InvalidPhone = define_application_error(1001, '无效的手机号')
InvalidEmail = define_application_error(1002, '无效的邮箱')
InvalidIdentity = define_application_error(1003, '无效的手机号或邮箱')
InvalidVerifyCode = define_application_error(1004, '验证码错误')
PhoneExists = define_application_error(1005, '手机号已注册')
EmailExists = define_application_error(1006, '邮箱已注册')
RateExceeded = define_application_error(1007, '请求太频繁，请稍后再试')
