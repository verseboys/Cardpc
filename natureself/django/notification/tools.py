from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail.message import forbid_multi_line_headers
from django.core.mail.utils import DNS_NAME
from django.core.mail import get_connection
from django.utils import timezone

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate, make_msgid
from email import encoders

from bs4 import BeautifulSoup
import htmlmin
import magic

from premailer import Premailer
premailer = Premailer()

import logging
logger = logging.getLogger(__name__)

from .models import Email, send_sms

DRYRUN = getattr(settings, 'EMAIL_DRY_RUN', False)

"""
Django 本身提供了很好用的发送邮件的功能。但是我们希望所有程序发出的邮件都可以被存档以备后续查阅，
因此我们重新封装了一套方法，使用这套方法发送的邮件都会被保存到数据库中，同时我们提供了查询的后台。

我们原本封装了一个 `send_mail` 函数，其调用方法兼容 Django 的 `send_mail`，但实践中发现，
Django 封装的 `send_mail` 还是不太好用，例如不支持附件、内嵌图片，例如 `recipient_list` 必须传
一个数组等等。如果要发送比较复杂的邮件，则需要使用 EmailMessage 或 EmailMultiAlternatives 来手动
构造邮件，使用复杂程度很高。Django 的封装毕竟要满足许多 general 的需求，因此封装程度并不是很高。

我们根据我们具体的业务场景，对发送邮件的功能进行了更高层次的封装，以简化使用。对于一些特殊场景，
我们可能会提供单独封装的函数，而不是让 send_mail 一个函数变得更加通用，从而控制学习、使用的成本。

我们的一般场景需求如下：
* 不需要纯文本邮件，总是发送 HTML 格式的邮件，即使内容并不需要格式
* 我们可能需要用到内嵌图片，可能需要发送附件
* 我们希望可以更容易的构造邮件内容，例如不要在 python 代码中构造 HTML 内容，而是使用 Django 的网页模板来构造
* 大多数时候，我们发送的邮件只需要一个收件人，发信人可以默认或按需指定，不需要抄送、密送

因此我们封装了 send_mail 函数，有以下几种调用方式：

    # 发送网页内容的邮件，content 为「正文」内容，其中：
    # to 可以是单个地址，也可以是多个地址的数组
    # from_email 可以省略，如果省略，默认使用 settings.DEFAULT_FROM_EMAIL
    send_mail(to, subject, content=content, from_email=from_email)

    # 发送纯文本内容的邮件，content 为纯文本。由于我们总是将内容的 Content-Type 标记为 text/html
    # 客户端在渲染时，「换行」无法被正确的渲染，因此我们会把内容用 <pre></pre> 包住
    send_mail(to, subject, content=content, plain=True)

    # 发送网页内容的邮件，使用 Django 的模板系统来渲染内容
    # 函数内会处理好内嵌图片，所有图片请使用 {% static %} 引入
    send_mail(to, subject, template='path/to/template.html', context={...})

    # 可以通过 attachments 参数来带附件，其中 attachment 是一个三元组：
    #   (filename, content, mimetype)
    #  * filename: 附件显示的文件名
    #  * content: 可以是 bytes 类型，为附件的内容
    #  * mimetype: 文件的 ContentType，如果为 None，则程序会尝试自动检测
    send_mail(to, subject, content, attachments=[...])

    # 发送自己构造的网页内容的邮件，并需要内嵌图片，其中 image 是一个三元组：
    #   (content-id, content, mimetype)
    #  * content-id 为网页中引用图片时使用的 cid
    #  * content、mimetype 与 attachment 相同
    # XXX 不建议这样使用，我们发送 HTML 邮件时，应该尽量使用 Django 模板来构造邮件内容
    send_mail(to, subject, content, images=[...])
"""

def send_mail(to, subject, from_email=None,
        content=None, plain=False, template=None, context=None, request=None, images=None, attachments=None,
        ):

    message = EmailMessage(
            to, subject, from_email=from_email,
            content=content, plain=plain,
            template=template, context=context, request=request,
            images=images, attachments=attachments,
        )

    return message.send()

class EmailMessage:
    """
    构造待发送的邮件。

    该类提供了 `encoding`, `from_email`, `recipients()`, `message()` 等属性、方法，
    主要是为了兼容 Django 的 Email Backend，从而我们无需自己实现 send() 函数，无需
    自己管理 connection。
    """

    encoding = settings.DEFAULT_CHARSET

    def __init__(self, to, subject, from_email=None,
            content=None, plain=False, template=None, context=None, request=None, images=None, attachments=None,
            ):

        # 调用时，应该提供 content 或 template 二者之一（不能两个都不提供或两个都提供）
        # 没有传值或者传递空字符串都算是没有提供的情形。我们不允许 content 为空字符串。
        if (not content and not template) or (content and template):
            raise ValueError('Must provide one and only one of "content" or "template"')

        if content:
            content = f'<pre>\n{content}\n<pre>' if plain else content
        else:
            content, images = self.render_content(template, context=context, request=request)

        content, images = self.sanitize_content(content, images)

        self.to = to if isinstance(to, list) else [str(to)]
        self.subject = subject
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.content = content
        self.images = images
        self.attachments = attachments

    def message(self):
        msg_root = MIMEMultipart('mixed')
        msg_root['Subject'] = forbid_multi_line_headers('Subject', self.subject, 'utf-8')[1]
        msg_root['From'] = forbid_multi_line_headers('From', self.from_email, 'utf-8')[1]
        msg_root['To'] = forbid_multi_line_headers('To', ', '.join(self.to), 'utf-8')[1]
        msg_root['Date'] = formatdate(localtime=settings.EMAIL_USE_LOCALTIME)
        msg_root['Message-ID'] = make_msgid(domain=DNS_NAME)

        msg_content = MIMEMultipart('related')
        msg_root.attach(msg_content)

        msg_text = MIMEText(self.content, 'html', 'utf-8')
        msg_content.attach(msg_text)

        if self.images:
            for image in self.images:
                msg_content.attach(self.create_inline_image(*image))

        if self.attachments:
            for attachment in self.attachments:
                msg_root.attach(self.create_attachment(*attachment))

        self.patch_message(msg_root)
        return msg_root

    def send(self):
        email = Email.objects.create(
                subject = self.subject,
                from_email = self.from_email,
                recipients = self.recipients(),
                content = self.content,
                message = self.message(),
                )

        exc = None

        email.sent_at = timezone.now()
        if DRYRUN:
            email.status = Email.STATUSES.dryrun
        else:
            try:
                connection = get_connection()
                connection.send_messages([self])
            except Exception as e:
                email.status = Email.STATUSES.failed
                exc = e
            else:
                email.status = Email.STATUSES.success
        email.save()

        if exc:
            logger.fatal('Error while sending email: %s', exc)
            raise exc

        return email

    def recipients(self):
        return self.to

    def patch_message(self, message):
        """
        Django 中 EmailBackend 在  send_messages() 中会调用 message.as_bytes(linesep='\r\n')，
        然而 Python 中 email.message.Message 的 as_bytes() 方法不支持 linesep 参数。
        我们这里 Patch 一下 Python 中的方法。
        """
        old_as_bytes = message.as_bytes
        message.as_bytes = lambda **kwargs: old_as_bytes(message)

    def sanitize_content(self, content, images=None):
        """
        规范化 content 中的内容。

        * 如果 content 中引用了外部图片，记录 Warning 日志
        * 如果 content 中引用了不存在的内嵌图片，抛出异常
        * 如果 images 中有图片没有被引用，记录 Warning 日志，并删除
        * 将 embedded css 改成 inline css （许多邮件客户端不支持 embedded css）
        * minify html

        返回修改后的 content 和 images （不会对原 images 数组进行原地修改）。

        将来可能会进行其它检查，例如删除所有 <script> 标签，以及根据实践来禁用一些邮件中无效的 HTML 标签。
        """

        provided_images = {
                image[0]: dict(content_id=image[0], content=image[1], mimetype=image[2], used=False)
                for image in images or []
                }

        soup = BeautifulSoup(content, 'html.parser')
        for img in soup.find_all('img'):
            if not img.has_attr('src'):
                logger.warning(f'Find <img> using external image: {img}')
                continue

            src = img['src']
            if not src.startswith('cid:'):
                logger.warning(f'Find <img> using external image: {img}')
                continue

            content_id = src[4:].strip()
            if content_id not in provided_images:
                raise ValueError(f'<img> referenced a non-exist image: {img}')

            provided_images[content_id]['used'] = True

        return_images = []
        for content_id, image in provided_images.items():
            if not image['used']:
                logger.warning(f'Provided image with content-id={content_id} not used, not attaching it to email')
            else:
                return_images.append((image['content_id'], image['content'], image['mimetype']))

        content = premailer.transform(content)
        content = htmlmin.minify(content)

        return content, return_images

    def render_content(self, template, context=None, request=None):
        content = render_to_string(template, context=context, request=request)
        images = []

        soup = BeautifulSoup(content, 'html.parser')
        for img in soup.find_all('img'):
            src = img['src']
            if not src.startswith(settings.STATIC_URL):
                # if img.src is not a local static url, don't do anything, and later sanitize_content() will warn on it
                continue

            # TODO, should support settings.MEDIA_URL

            # NOTES on working with django static files
            # * django.contrib.staticfiles.finders
            #   finders.find('app/image/awesome.png') -> returns the finded file's filesystem path
            # * django.templatetags.static.static
            #   static('app/img/awesome.png') -> returns {STATIC_URL}app/img/awesome.png
            # so, for the reversed approach, we first left strip off STATIC_URL, then use finders to find the filesystem path
            static_name = src[len(settings.STATIC_URL):]
            static_file = finders.find(static_name)

            content_id = str(len(images) + 1)
            img['src'] = f'cid:{content_id}'

            with open(static_file, 'rb') as fp:
                content = fp.read()
                mimetype = magic.from_buffer(content, mime=True)
                images.append((content_id, content, mimetype))

        return str(soup), images

    def create_attachment(self, filename, content, mimetype):
        mimetype = mimetype or magic.from_buffer(content, mime=True)
        maintype, subtype = mimetype.split('/', 1)
        if maintype == 'text':
            part = MIMEText(content, _subtype=subtype)
        elif maintype == 'image':
            part = MIMEImage(content, _subtype=subtype)
        elif maintype == 'audio':
            part = MIMEAudio(content, _subtype=subtype)
        else:
            part = MIMEBase(maintype, subtype)
            part.set_payload(content)
            encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=filename)

        return part

    def create_inline_image(self, content_id, content, mimetype):
        mimetype = mimetype or magic.from_buffer(content, mime=True)
        maintype, subtype = mimetype.split('/', 1)
        assert maintype == 'image'
        part = MIMEImage(content, _subtype=subtype)
        part.add_header('Content-Disposition', 'inline')
        part.add_header('Content-ID', f'<{content_id}>')

        return part
