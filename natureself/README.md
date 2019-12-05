# natureself 公共 python 模块

本项目包含一些在内部项目中公共使用的 python 模块，目前大多数模块均为在 Django 中使用。

目前有以下这些模块：

* [`natureself.django.core`](./doc/natureself-django-core.md) 包含一些在 Django 中使用的常用辅助性代码
* [`natureself.django.media`](./doc/natureself-django-media.md) 关于图片、文件、视频等功能的基础封装，所有项目中使用到上传图片、文件等功能时都应该使用
* [`natureself.django.notification`](./doc/natureself-django-notification.md) 发送短信、邮件、微信等通知
* [`natureself.django.account`](./doc/natureself-django-account.md) 登录相关的公共库
* [`natureself.django.otp`](./doc/natureself-django-otp.md) OTP 模块（One Time Password，简单理解为短信/邮件验证码）
* [`natureself.webapp`](./doc/natureself-webapp.md) 前端相关工具
* [`natureself.admin`](./doc/natureself-admin.md) 管理后台框架
* [`natureself.ums`](./doc/natureself-ums.md) UMS 相关功能模块

## 如果在 Django 项目中使用？

在已有的 Django 项目中，首先将本项目的代码复制到 `natureself/` 目录（可以用下面*初始引入*相关的 Git 命令引入，也可以直接手动把本项目代码拷贝进去（注意拷贝进去后把 `natureself/.git/` 目录删除）。

在 `nsproject/settings.py` 中，`INSTALLED_APPS` 里添加以下内容：

```py
INSTALLED_APPS = [
    ...
    # 如果该项目有用户前端，请加入 n.d.webapp
    'natureself.webapp',
    # 如果该项目需要管理后台，请加入 n.d.admin
    'natureself.admin',
    # 请总是加入 n.d.account，并使用这里面提供的登录 API
    'natureself.django.account',
    # 如果项目中需要用户上传图片、附件等，请加入 n.d.media
    'natureself.django.media',
    # 如果项目中需要发短信、发邮件，请加入 n.d.notification
    'natureself.django.notification',
]
```

在 `nsproject/urls.py` 中加入以下内容：

```py
urlpatterns = [
    ...
    path('', include('natureself.django.account.urls')),
    path('', include('natureself.django.notification.urls')),
    path('', include('natureself.django.media.urls')),
]
```

如果项目有用户前端，则创建一个文件 `nsproject/webapp.js`，文件中可以配置多个 entry 文件，`entry` 的值会传递给 webpack，webpack 在编译时会编译相应的文件。

```js
module.exports = {
  // configure entries
  entry: {
    cardpc: 'cardpc/webapp/index.js',
  },
}
```

如果项目需要管理后台，则创建一个文件 `nsproject/admin.js`，内容类似：

```js
import logo from '@natureself/assets/logo/natureself.svg'
import NatureselfDjangoAccount from 'natureself/django/account/admin/app.js'
import NatureselfDjangoMedia from 'natureself/django/media/admin/app.js'
import NatureselfDjangoNotification from 'natureself/django/notification/admin/app.js'

export default {
  apps: {
    NatureselfDjangoAccount,
    NatureselfDjangoMedia,
    NatureselfDjangoNotification,
  },
  logo,
  title: '管理后台',
}
```

这里面可以配置几样东西：
* 管理后台上显示的 Logo 图片
* 管理后台上显示的标题
* 注册所有提供了管理后台模块的 django app，每一个 app 需要提供一个 `app.js` 文件，可以上面列出的三个 n.d.xxx 里面的文件可以作为参考。

如果有用户前端，还需要在 `nsproject/settings.py` 中增加以下配置：

```py
# webpack_loader 这个第三方库，可以读取 webpack 构建后输出的 stats 文件，
# 知道编译生成的 entry 资源的文件名，从而在 Django 模板网页中使用
INSTALLED_APPS += [
    'webpack_loader',
]

# 注意，以下段落中出现的 DEBUG、BUILD_DIR 的值都需要提前赋值，可以参考 edc-next 项目中的写法
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': os.path.join(BUILD_DIR, 'webpack-stats-webapp.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

# 以下是配置静态文件资源的，照抄就可以了，基本上每个项目都一样
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BUILD_DIR, 'webapp'),
    os.path.join(BASE_DIR, 'natureself/assets/'),
]

STATIC_ROOT = os.path.join(BUILD_DIR, 'static')
STATIC_URL = '/static/'

# 如果用了 n.d.media 或 n.d.notification，请添加 MEDIA 相关的配置
# 这里的目录用来保存用户上传的文件，使用 n.d.notification 时，发送的每一封邮件都会有本地存档，也是保存在 MEDIA_ROOT 中
MEDIA_ROOT = os.path.join(BASE_DIR, 'data')
MEDIA_URL = '/media/'
```

如果使用 `n.d.notification`，还需要在 `nsproject/settings_local.py` 中加入短信和邮件相关的配置：

```py
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
```

在项目的 `requirements.txt` 中加入：

```
-r natureself/requirements.txt
...
```

这样，在 `pip install -r requirements.txt` 时，会把 `py-natureself` 依赖的包都安装上。

创建 `package.json` 文件，可以拷贝 natureself/package.example.json，将里面的 `{{PROJECT}}` 修改掉。里面重要的字段：
* `devDependencies` 依赖的包，由于 package.json 不像 python 的 requirements.txt 那样，因此我们无法提供一个文件通过某种功能 include 的方式来自动引入，只能每个项目手动管理了
* `scripts` 这里面定义了四条命令，分别是 `build-admin`, `serve-admin`, `bulid`, `serve`，其中
  * `build`、`build-admin` 用于生产环境，大家在本地开发是一般无需使用。运行后，会自动用相应的 webpack.config.js 来构建
  * `serve`、`serve-admin` 用于本地开发，这个命令会启动 webpack-dev-server，不会退出，当代码有更新时，会自动通知网页进行热更新。

## Git 相关命令

**由于使用的命令比较复杂，我不太清楚IDE里面是否可以实现，因此所有操作可以由我（张成）来操作。**

本项目在将来会打包成私有包，可以使用 `pip install` 来安装。但是在近期，该项目尚未稳定，为了方便日常开发调试，我们使用
`git subtree` 的方式将该项目代码内置到所有需要的其他项目中。

`git subtree` 的使用方法可以参考[这篇教程](https://medium.com/@porteneuve/mastering-git-subtrees-943d29a798ec) 。
这里仅列出本项目日常使用的方法。

### 初始引入

在目标项目中，首次引入 natureself 这个包，可以使用下面的命令：

```sh
git remote add py-natureself git@git.evahealth.net:natureself/py-natureself.git
git fetch py-natureself
git merge --squash -s ours --no-commit --allow-unrelated-histories py-natureself/master
git read-tree --prefix=natureself/ -u py-natureself/master
git commit -m "[subtree] add py-natureself"
```

### 更新 natureself 目录中的代码

当本项目（py-natureself）有更新之后，在目标项目中要可以用以下命令更新本地的代码：

```sh
git pull -s subtree -X theirs py-natureself master --squash
git commit -m '[subtree] sync py-natureself'
```

### 反向推送 natureself 目录中的修改

反向推送代码比较麻烦，大致步骤：

* 本地创建一个分支，该分支基于 py-natureself/master （该分支可以一直维护着）
* 将目标项目中相应的 commit 给 cherry-pick 过来
* push 代码

具体代码如下（实际使用时请根据具体情况调整）：

```sh
git checkout -b backport-py-natureself py-natureself/master
git cherry-pick --strategy=subtree {commit-sha}
# 在推送前，检查确认一下 log 是否符合预期
git log --oneline
# 推送到一个新的分支，然后创建 Merge Request
git push py-natureself backport-py-natureself:{new-branch}
```
