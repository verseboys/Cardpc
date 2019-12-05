# natureself.django.account

提供账号相关的网页 view、API view。包括：

* 登录网页、API
* 登出网页、API
* 重置密码网页、API (暂未实现)
* UMS 集成
* 微信集成
* 用户角色定义

## 使用方法

在 `INSTALLED_APPS` 中添加：

```python
INSTALLED_APPS = [
    ...
    'natureself.django.account',
    'natureself.django.notification', # 重置密码时发送短信、邮件需要使用
    'natureself.django.admin',        # 提供了一个账号管理后台
    ...
]
```

请确认 MIDDLEWARE 中包含：

```python
MIDDLEWARE = [
    ...
    'natureself.django.core.middleware.DecodeBodyJsonMiddleware',
    ...
]
```

`natureself.django.notification` 所需要的配置，请参考 [`natureself.django.notification`文档](natureself-django-notification.md)。

其他配置：

```
# 每一个项目可以自行实现登录、登出、重置密码的网页模板，模板说明见下文
# 以下配置均为可选配置，默认使用 natureself.django.account 自带的模板文件
LOGIN_TEMPLATE = 'account/login.html'
LOGOUT_TEMPLATE = 'account/logout.html'
RESET_PASSWORD_TEMPLATE = 'account/reset_password.html'

# 重置密码时，需要使用缓存系统来记录生成的临时 TOKEN，因此需要配置缓存
# 缓存的配置请参考 Django 官方文档：https://docs.djangoproject.com/en/2.1/topics/cache/#setting-up-the-cache
# 也可参考 nsproject/settings_local.example.py （大多数项目中该文件里应该有样例）
# AUTH_CACHE 可以配置使用哪一个 CACHE，默认使用 default
AUTH_CACHE = 'default'
```

在 `nsproject/urls.py` 中加入：

```python
urlpatterns = [
    path('', include('natureself.django.account.urls')),
    ...
]
```

这会注册以下 URL：

```
name=api_login:           POST /api/account/login
name=api_logout:          POST /api/account/logout
name=api_get_info:        GET  /api/account/info
name=api_reset_password:  POST /api/account/reset_password
name=page_login:          GET  /account/login/
name=page_logout:         GET  /account/logout/
name=page_reset_password: GET  /account/reset_password/
```

## User Model

### 用户角色

对于一般网站来说，账号至少会有三类角色：普通用户、管理员、超级用户。我们约定角色名称：

* 普通用户：无名称
* 管理员：`admin`，在 Django 用户 Model 中，`is_staff` 如果为 `True`，表示该用户有 `admin` 这个角色
* 超级用户：`superuser`，在 Django 用户 Model 中，`is_superuser` 如果为 `True`，表示该用户有 `superuser` 这个角色

一个用户的角色使用数组来表示，例如 `some_user.roles == ['admin', 'superuser']`，表示该用户是管理员、也是超级用户。
我们约定所有用户都有普通用户角色，因此无需专门为普通用户命名。

如果一个项目使用了自定义的 User Model，那么自定义 Model 应该：

* 要么继承自 Django 的 `AbstractBaseUser`，因此也有 `is_staff`、`is_superuser` 属性，并且网站也使用这两个属性
* 要么定义 `roles` 属性，自行定义角色，例如：

```python
class CustomUser(models.Model):
    ...

    @property
    def roles(self):
        return ['role1', 'role2']
```

如果我们发现用户 model 有 `roles` 属性，则会直接使用该属性，否则将根据 `is_staff`、`is_superuser` 自动识别。

我们对角色名称不做要求或限制，在 `django.natureself.account` 中也不会依赖任何特定名称的角色。

角色主要用于一些权限相关的地方，例如管理后台登录时，要求管理员才可登录，管理后台的部分侧边栏菜单可能需要特定角色才有权限，
具体每一处依赖的角色都由具体项目在调用出指定。

不过我们建议，如果某项目对用户角色没有复杂需求，可以直接使用这里默认的 `admin` 和 `superuser`。
如果某项目需要使用较复杂的角色体系，也尽量保留使用 `admin` 和 `superuser`，使得我们所有的项目中保持一致。

### serialize() 方法

在登录、获取用户信息等 API 中，需要返回用户信息。按照我们以往项目中的习惯，我们给每一个 model 定义一个 `serialize()` 方法，
该方法的签名如下：

```python
class SomeModel(models):
    def serialize(self, to_dict=True, **kwargs):
        pass
```

其中，`to_dict` 如果为 `True`，则该函数返回一个字典，如果为 `False`，则返回该字典的 JSON 字符串（str 类型，非 bytes 类型）。

在 `natureself.django.account` 中需要返回用户信息时，会检测用户 model 是否实现了 `serialize()` 方法，如果实现了会直接使用，
如果没有实现，则会默认序列化 `username` 字段。

此外，在序列化时，还会加入 `roles` 字段。如果用户 model 实现了 `serialize()` 且 `serialize()` 返回的内容中没有 `roles` 字段，
那么 `natureself.django.account` 会自动加入 `roles` 字段。

## 自定义模板

TODO

## 登录流程

无论是使用内置默认模板还是自定义模板，登录的实际操作都使用 API 的方式。

用户只有满足以下条件之后才能登录：

* 提供的登录凭证（如账号+密码、手机号+验证码等等）正确，用户存在
* 用户的 `is_active` 字段为 True
* 如果登录请求中带有 `role` 参数，则用户的角色中必须包含该角色

只要上述任一条件不满足，登录失败。

## 重置密码流程

TODO
