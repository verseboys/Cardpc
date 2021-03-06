# 短信/邮件验证码

## 需求分析

可用于注册验证、登录验证以及其他验证场景。基础需求描述：

* 同一个手机号（或邮箱，下同）1 分钟内最多只发送一条短信（如果有多个浏览器、设备，也只能发送一条）
* 同一个浏览器，1 分钟内最多只发送一条短信
* 验证码有效期 10 分钟，在有效期内如果多次生成，则每次生成的验证码相同
* 一个验证码最多有 5 次验证尝试，验证次数超过 5 次，或已使用，则立即失效

注意注册验证码与登录验证码不同。登录验证码，实际上叫 OTP（One Time Password），一次性密码。
注册验证码的用途则是校验当前用户是否拥实际控制其提供的手机号。在业务层的区别：

注册：

* 用户请求验证码
* 服务器发送验证码
* 用户填入验证码，前端会校验验证码是否正确（第一次校验）
* 用户填写完其他信息，点击注册（此时服务器需要再次校验）

登录：

* 用户请求验证码（一次性密码）
* 服务器发送验证码
* 用户填入验证码，前端不会校验此验证码
* 用户点击登录（服务器进行一次校验）

对于注册这种场景，在用户第一次校验成功后，我们可以不标记已使用，也不增加校验次数计数。
只有在最后一次校验时，在数据库中。

在上述描述中出现的几个数字，我们都做成可以配置的：
* 1 分钟：在代码中称为静默时长（silent duration），静默期内不会生成新的验证码，也不会发送短信
* 10 分钟：在代码中称为有效时长（valid duration），有效期内不会生成新的验证码，但会重新发送短信
* 5 次尝试：在代码中称为失败校验次数（verify count），允许的失败校验次数，用来防止用户通过暴力穷举的方式找到正确的验证码

在实际实现中，我们增加一个概念：会话（session），一个会话可以简单理解为一个浏览器。
用户换一个浏览器、或使用浏览器的不同 profile（如普通模式和隐身模式）、或不同的设备，
都是两个不同的会话。

增加会话的概念主要有两方面用途：
* 静默期同时考虑手机号和会话。即同一个手机号，即使同时打开多个浏览器，一分钟内也只能发送一条短信。
并且，同一个浏览器中，用户频繁更改手机号，一分钟内也只能发送一条短信。
* 在一个会话中生成的验证码，只允许在这个会话中使用。例如用户在PC浏览器上发送了注册验证码，
此时打开手机浏览器进入注册页面，将收到的验证码输进去是不能用的。这使得不同浏览器发送的验证码相互独立，
同时也可以防止窃听攻击（例如黑客木马劫持了用户手机的短信，在收到验证码之后，自动黑客的电脑上尝试使用）。

在静默期中，用户再次请求发送验证码时，又分为两类细分情形：
* 手机号、会话完全相同，这有可能是前端代码BUG（如用户双击导致发送两次），也可能是用户刷新网页“解除”了倒计时
并再次点击获取验证码。此时我们可以像正常情况一样告诉用户短信已发送。
* 手机号相同、会话不同，或者手机号不同、会话相同，此时需要告诉用户“请求太频繁，请1分钟后再请求”。

在静默期后、有效期内，用户再次请求发送验证码时，可能是由于用户运营商问题没有及时收到短信，
此时我们不生成新的验证码，而是直接重发一遍原来的验证码，并重置有效期。这样做的目的是防止
用户一下子收到两条短信，两个不同的验证码不知道填哪一个，我们后端的处理逻辑也会更加复杂。

除静默期的场景外，任何其他原因导致没有实际发送短信的（例如手机号不正确，被系统判断为恶意的请求等），
都无需告知用户发送失败，只需要像正常情况一样返回“短信已发送”即可。

## 使用方法

### 发送验证码
```py
from natureself.django.otp.tools import USAGES, generate_code, GENERATE_RESULTS

vcode, result = generate_code('sms', request, '13912345678', USAGES.register)
if vcode:
    # 当 vcode 不为 None 时，有两种可能，一种是正常发送了验证码，
    # 一种是在静默期内，手机号、会话相同，没有重新发送验证码，
    # 这两种情况下，我们都提示用户验证码已发送
    return api.ok(message='短信已发送')
elif result == GENERATE_RESULTS.silent:
    reutrn api.bad_request(message='发送请求太频繁')
else:
    # vcode == None, result != silent，此时是发生了其他错误，
    # 这些错误我们都不向用户暴露，而是假装正常
    return api.ok(message='短信已发送')
```

### 校验验证码
```py
from natureself.django.otp.tools import verify_code, USAGES

# 最后一个参数，mark_used_on_success = False，表示正确时不要标记该验证码已用
valid = verify_code('sms', request, '13912345678', USAGES.register, '123456', False)
if valid:
    return api.ok(message='验证码正确')
else:
    return api.bad_request(message='验证码错误')

# 在明确的最后一次使用（如注册、登录的 API 中），设置 mark_used_on_success = True，
# 这样如果成功了，立即标记该验证码失效。如果失败，会增加校验计数，但不标记已使用。
valid = verify_code(..., True)
if valid:
    user = create_user(...)
    return api.ok(data=user)
else:
    return api.bad_request(message='验证码错误')
```
