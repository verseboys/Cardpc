这里提供发送短信、邮件的封装函数。所有发出去的短信、邮件都会记录在数据库中。

## 用法

首先需要在 `INSTALLED_APPS` 中加入 `natureself.django.notification` 。

要发送短信，需要在 `settings_local.py` 中加入以下配置：

```py
ALI_SMS_DRY_RUN = True
ALI_SMS_ACCESS_KEY_ID = '................'
ALI_SMS_ACCESS_KEY_SECRET = '..............................'
```

在测试环境中，建议不配置阿里云实际地址，而是设置 `ALI_SMS_DRY_RUN` 为 `True`，这样不会实际发出短信，而是会打印到终端。

要发送邮件，需要在 `settings_local.py` 中加入以下配置：

```py
EMAIL_DRY_RUN = True
EMAIL_HOST = 'smtp.natureself.site'
EMAIL_PORT = '25'
```

同样，如果 `EMAIL_DRY_RUN` 为 `True`，邮件就不会发送，而是会打印到终端（打印的是邮件的 raw 格式，人类几乎不可读）。
`EMAIL_DRY_RUN` 为 `False` 时，上述配置的地址可以正常发送邮件，但请注意发送的内容，不要像 spam，也要注意频率，
这实质上还是使用的第三方服务，仍然有被封禁的风险。

### 发送短信

```py
from natureself.django.notification.tools import send_sms
from natureself.django.notification.models import AliSms

send_sms(
    phone_numbers = '13900000001',
    signature_name = AliSms.SIGNATURES.dayuceshi,
    template_code = AliSms.TEMPLATES.login,
    template_param = dict(code='123456'),
)
```

### 发送邮件

强烈建议先阅读一下[邮件的基本知识](./email-basics.md)

```py
from natureself.django.notification.tools import send_mail

# 发送网页内容的邮件，content 为「正文」内容，其中：
# * to 可以是单个地址，也可以是多个地址的数组
# * content 为 html 源码
# * from_email 可以省略，如果省略，默认使用 settings.DEFAULT_FROM_EMAIL
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
#  * content: 是 bytes 类型，为附件的内容
#  * mimetype: 文件的 ContentType，如果为 None，则程序会尝试自动检测
send_mail(to, subject, content, attachments=[...])

# 发送自己构造的网页内容的邮件，并需要内嵌图片，其中 image 是一个三元组：
#   (content-id, content, mimetype)
#  * content-id 为网页中引用图片时使用的 cid
#  * content、mimetype 与 attachment 相同
# XXX 不建议这样使用，我们发送 HTML 邮件时，应该尽量使用 Django 模板来构造邮件内容
send_mail(to, subject, content, images=[...])
```

**请不要在 Python 代码中手动构造 HTML 邮件内容！**

**请不要在 Python 代码中手动构造 HTML 邮件内容！**

**请不要在 Python 代码中手动构造 HTML 邮件内容！**

请使用 Django 的模板系统来构造邮件内容，这样既方便开发时预览邮件的内容，又可以避免代码中有大量字符串拼接操作。
邮件模板请保存在 `$PROJECT_ROOT/$app/templates/$app/emails/xxx.html` ，其中 `$app` 为 Django 中的 app 的名字，
例如在 `medieco-next` 项目中，医咖会的大多数代码都在 `medieco` 这个 app 中。这样，这个模板的名字就是：
`$app/emails/xxx.html`。

假设这个模板是一个网页的模板，要渲染这个网页，可以这样做：

```py
from django.shortcuts import render

def some_view(request):
    context = ...
    return render('$app/emails/xxx.html', context=context)
```

在发邮件时也是类似的用法：

```py
from natureself.django.notification.tools import send_mail

send_mail('zhangsan@example.com', '测试邮件', template='$app/emails/xxx.html', context={...})
```

`natureself.django.notification` 提供了一个专门用于预览邮件模板的地址：

```
http://localhost:8000/debug/preview-email/?template=${template-name}&var1=xxx&var2=xxx
```

其中，`${template-name}` 即模板的名字，例如前面的 `$app/emails/xxx.html`，剩余其他所有 querystring
都会作为 `context` 传递给模板引擎。当然，这个地址仅适合于比较简单的 context，如果你的模板中需要使用到
比较复杂的 context （例如有些变量是字典或者 Python 对象），那么你只需要在开发时临时写一个 view 用来渲染
模板，观察效果即可。

关于邮件 HTML 的限制：

* **不支持 JS，因此请不要在 HTML 中加入任何脚本**
* **不支持外部 css，因此请不要用 `<link>` 标签加入任何外部 css 文件**
* **不支持外部图片，因此请不要用 `<img src="http://...">` 加入任何外部图片**，
但是可以用 `{% static ... %}` 来引入我们自己的图片，`send_mail()` 会自动识别出这些图片，
并将这些图片以正确的方式插入邮件中。
* 许多邮件客户端不支持内嵌css，即通过 `<style>` 标签引入的 css，因此我们的 `send_mail()`
中自动将网页中的内嵌css都转化成了 inline css，即直接写在元素标签的 `style="..."` 属性中。
因此，在邮件模板中可以使用 `<style>`，并且鼓励使用，因为这会使得代码很美观。
* 许多邮件客户端不支持 data url，即形如：`<img src="data;image/png;base64,...">` 这样的，
因此 **请不要使用 data url**

关于邮件模板，可以参考 [example-email.html](/django/notification/templates/notification/emails/example-email.html)
