# `n.d.account` 设计参考

n.d.account 期望可以尽量做到跨项目通用，因此其 API 在设计时需要考虑到通用性，
但又不应该将参数设计的过于复杂，以至于每一个项目使用时都要做许多配置。

**兼容性** 我们应该兼容 Django 自带的 User 系统，即一个新项目使用 Django 的
User 系统，可以不做任何定制就使用 n.d.account。

**定制性** 针对泽创内部项目，我们可以预定一些基本规范，即以后大多数项目中用
户模型都会具有的共同特点。

## 登录 `POST /api/account/login`

**登录 API 首要考虑的是兼容 Django 的 Authentication 系统**。

在 Django 中，不鼓励直接在 view 方法中直接对比用户密码。而是使用 Authentication
Backend 来校验用户密码。这样做的目的是方便扩展、支持多套校验源。

例如在 edc-next 中，我们支持使用 UMS 或本地校验，只需要分别实现一个 Backend，
然后在 settings.py 中激活这两个 Backend 即可，login view 无需做任何改动。
也因此，`n.d.account` 提供的 login view 可以同时兼容 Django 的 User Model
以及 edc 中自定义的 User Model 和校验规则。

关于 Django 的校验系统，请参考官方文档
[auth 系统](https://docs.djangoproject.com/en/2.2/topics/auth/default/)
[定制 auth](https://docs.djangoproject.com/en/2.2/topics/auth/customizing/)
