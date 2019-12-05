from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import re

"""
一些与校验有关的帮助函数。

注：这个文件名取的不是特别好，因为 Django 中本来就有 Validator 的概念，见
[官方文档](https://docs.djangoproject.com/en/2.2/ref/validators/)，
此文件并非是对 Django Validator 的扩展，也不兼容其使用方式。
但是我暂时没有想到更好的路径、文件名来保存这些东西。
"""

def is_valid_email(email):
    """
    检查是否是合法的邮箱，返回 True/False

    正二八经的检查分三级：
    * 正则式检查，看字面上是否是一个合法的地址
    * 检查 MX 服务器是否存在、且可以连接，这可以毙掉随便写的假邮箱
    * 连接 smtp 服务器，询问服务器该地址是否存在。我不清楚这个方法
      的可靠性如何，我认为 smtp 服务器并不总是要告诉询问者这个信息。

    第三方实现：
    * [validate_email](https://github.com/syrusakbary/validate_email)，
      这个第三方库支持三级检查
    * 借用 [Django EmailValidator](https://stackoverflow.com/a/3218128)
    * 使用 [email.utils.parseaddr()](https://stackoverflow.com/a/14485817)
    * 自行用正则式检查

    注意，每一种方式都会有一些局限性，综合考虑实现成本、使用便利性
    （例如我们测试时，需要能够使用一些假的邮箱），我们选择用 Django
    EmailValidator 来校验。
    """
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

"""
中国内地手机号段数据
数据来源：https://zh.wikipedia.org/wiki/中国内地移动终端通讯号段
更新日期：2019-04-27

中国移动： r'^(134|13[5-9]|147|15[0-27-9]|178|18[2-478]|198)[0-9]{8}$'
* 134[0-8] 为简化正则式，正则式中不对比第4位，即匹配 134*
* 13[5-9]
* 147
* 15[0-2]
* 15[7-9]
* 178
* 18[2-4]
* 18[7-8]
* 198

中国联通： r'^(13[0-2]|145|15[56]|166|17[56]|18[56])[0-9]{8}$'
* 13[0-2]
* 145
* 15[56]
* 166
* 17[56]
* 18[56]

中国电信：r'^(133|1349|153|173|177|18[019]|19[19])[0-9]{8}$'
* 133
* 1349
* 149
* 153
* 173
* 1740[0-5] 卫星手机卡，不计入
* 177
* 180
* 181
* 189
* 191
* 199

综合： r'^(13[0-9]|14[579]|15[0-35-9]|166|17[35-8]|18[0-9]|19[189])[0-9]{8}$'
* 13[0-9]
* 14[579]
* 15[0-35-9]
* 166
* 17[35-8]
* 1740[0-5] 卫星手机卡，不计入
* 18[0-9]
* 19[189]
"""
_PHONE_PATTERN_CHINA_MOBILE = re.compile(r'^(134[0-8]|13[5-9]|147|15[0-27-9]|178|18[2-478]|198)[0-9]{8}$')
_PHONE_PATTERN_CHINA_UNICOM = re.compile(r'^(13[0-2]|145|15[56]|166|17[56]|18[56])[0-9]{8}$')
_PHONE_PATTERN_CHINA_TELECOM = re.compile(r'^(133|1349|153|173|177|18[019]|19[19])[0-9]{8}$')
_PHONE_PATTERN_CHINA = re.compile(r'^(13[0-9]|14[579]|15[0-35-9]|166|17[35-8]|18[0-9]|19[189])[0-9]{8}$')

def is_valid_phone(phone):
    """
    检查是否合法的中国内地手机号，返回 True/False
    """
    try:
        return True if _PHONE_PATTERN_CHINA.match(phone) else False
    except TypeError:
        # 当 phone 不是字符串时，会抛出 TypeError
        return False
