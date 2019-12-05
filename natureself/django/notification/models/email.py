from django.db import models
from django.utils.functional import cached_property
from django.utils import timezone
from django.conf import settings
from email.utils import parseaddr, collapse_rfc2231_value
from email import message, policy, message_from_file

import os
import uuid
import base64
import pathlib
from model_utils import Choices

class EmailManager(models.Manager):
    def create(self, subject, from_email, recipients, content, message, **kwargs):
        if isinstance(recipients, list):
            recipients = ', '.join(recipients)

        local_file = uuid.uuid4().hex
        local_path = f'{local_file[:2]}/{local_file}'
        local_abs_path = os.path.join(settings.MEDIA_ROOT, 'emails', local_path)
        local_abs_dir = os.path.dirname(local_abs_path)
        if not os.path.isdir(local_abs_dir):
            pathlib.Path(local_abs_dir).mkdir(parents=True, exist_ok=True)
        with open(local_abs_path, 'w+') as fp:
            fp.write(message.as_string())

        status = kwargs.pop('status', self.model.STATUSES.pending)

        return super().create(
                subject = subject,
                from_email = from_email,
                recipients = recipients,
                content = content,
                status = status,
                local_path = local_path,
                **kwargs,
                )

class Email(models.Model):
    """
    记录所有发送的邮件

    由于邮件体积可能很大（例如有数兆的附件），不适合全部保存在数据库中。我们将完整的邮件保存到文件中，
    而数据库中仅保存一些主要的 Header 以及邮件正文内容，用于检索、查询。

    此外，数据库中还会记录一些与发送有关的信息，例如发送时间、发送是否成功等等。
    """
    objects = EmailManager()

    # 邮件标题
    subject = models.TextField()
    # 发件人地址
    from_email = models.TextField()
    # 收件人地址
    # 这里指实际的收件人地址，不仅仅是 To Header 中的地址，不过只要是用 send_mail 发送的邮件，肯定是一致的
    recipients = models.TextField()
    # 邮件「正文」，HTML 格式（这是实际发送出去的邮件的正文部分的内容，即渲染之后的内容）
    content = models.TextField()

    # 邮件发送的状态
    # 目前我们的邮件使用同步发送的方式，即调用 send_mail() 会立刻发送，在发送结束后才会返回，
    # 但是将来我们可能会采用异步发送的方式，即 send_mail() 仅仅将邮件加入待发送队列，然后异步调度发送，
    # 从而可以实现频率限制等功能。
    STATUSES = Choices(
        # pending 表示已经将邮件加入待发送队列，等待被发送，现在使用同步发送的方式，邮件不会处于该状态
        ('pending', 'pending', '待发送'),
        # reject 表示由于某种原因拒绝发送，例如超过发送频率限制，或其他内部限制。目前没有实现这方面限制，所以不会处于该状态
        ('reject', 'reject', '拒绝发送'),
        # 表示已经通过 smtp 或者 http api 将邮件投递给了第三方邮件服务商，但服务商那边可能需要异步返回实际发送结果，
        # 我们获得这个结果前处于该状态。目前我们还没有碰到服务商需要异步返回结果的情况，所以目前不会处于该状态
        ('sent', 'sent', '已发送'),
        # 表示邮件已经发送成功（服务商没有返回错误）（但这并不代表邮件一定已经送达用户）。
        ('success', 'success', '发送成功'),
        # 表示在发送邮件时，服务商返回了错误
        ('failed', 'failed', '发送失败'),
        # 表示这封邮件仅仅是本地测试使用，没有真实发送出去
        ('dryrun', 'dryrun', '本地测试'),
    )
    status = models.TextField(choices=STATUSES)

    # 本地存储邮件的地址，改地址为相对路径，相对的根为 {MEDIA_ROOT}/emails
    local_path = models.TextField()

    # 调用 send_mail() 的时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 实际通过 smtp 或 http api 发送邮件的时间。目前我们使用同步发送的方式，因此 created_at 与 sent_at 相同（或只有极小的差别）
    sent_at = models.TextField()

    def __str__(self):
        return f'recipients: {self.recipients}, subject: {self.subject}'

    def parseaddr(self, addr):
        name, addr = parseaddr(addr)
        display = f'{name} <{addr}>' if name else addr
        return dict(name=name, address=addr, display=display)

    @cached_property
    def message(self):
        local_abs_path = os.path.join(settings.MEDIA_ROOT, 'emails', self.local_path)
        if not os.path.exists(local_abs_path):
            return None
        with open(local_abs_path) as fp:
            return message_from_file(fp, _class=message.EmailMessage, policy=policy.default)

    @cached_property
    def images(self):
        images = dict()

        if not self.message:
            return images

        for part in self.message.walk():
            if part['Content-Type'].startswith('image/') and 'Content-ID' in part:
                images[part['Content-ID'][1:-1]] = dict(
                        content_id = part['Content-ID'][1:-1],
                        mimetype = part['Content-Type'],
                        payload = part.get_content(),
                        )

        return images

    @cached_property
    def attachments(self):
        attachments = dict()

        if not self.message:
            return attachments

        for part in self.message.walk():
            if 'Content-Disposition' in part and part['Content-Disposition'].startswith('attachment'):
                filename = part.get_param('filename', header='Content-Disposition')
                if filename:
                    filename = collapse_rfc2231_value(filename)
                    attachments[filename] = dict(
                            filename = filename,
                            mimetype = part['Content-Type'],
                            payload = part.get_content(),
                            )

        return attachments

    @cached_property
    def content_with_inline_image(self):
        content = self.content

        if not self.images:
            return content

        for cid, image in self.images.items():
            b64content = base64.encodebytes(image['payload']).decode().replace('=', '%3D').replace('\n', '')
            content = content.replace(f'cid:{cid}', f'data:{image["mimetype"]};base64,{b64content}')

        return content

    def serialize(self, to_dict=True):
        data = {
                'id': self.id,
                'subject': self.subject,
                'from_email': self.parseaddr(self.from_email),
                'recipients': [self.parseaddr(r) for r in self.recipients.split(',')],
                'content': self.content_with_inline_image,
                'status': self.status,
                'created_at': self.created_at,
                'sent_at': self.sent_at,
                'attachments': [attachment['filename'] for attachment in self.attachments],
                }

        return data if to_dict else json.dumps(data, ensure_ascii=False)
