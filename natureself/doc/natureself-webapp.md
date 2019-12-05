这里提供构建前端所需的工具。

# 前端规范约定

我们目前每个项目可能有两个前端，用户前端和管理后台。我们鼓励：

* 管理后台使用 Vue SPA 的方式实现
* 用户前端使用 Django Template 直接渲染，我们鼓励在页面内使用 Vue 或其他框架。

当然，如果用户前端不涉及到 SEO 等需求（比如微信内应用），也可以使用 SPA 来实现。

管理后台的实现方式，我们已经提供了统一的框架，请参考 [natureself.django.admin](./natureself-django-admin.md)。

这篇文档重点讲用户前端实现时的规范和方法。

# 用法

创建 `package.json`，并安装依赖库。

**NOTE** 由于 package.json 不像 python 中的 requirements.txt 那样支持 `include`，因此 webapp 无法提供一个 package.json，
让网站项目去拓展，package.json 文件只能由网站项目自行维护。以下是目前 webapp 依赖的包，这个列表可能不完整，如果发现不完整，
请及时更新本文档：

```sh
npm install --save-dev \
    vue vue-router vuex \
    axios js-cookie \
    webpack webpack-cli webpack-merge webpack-dev-server \
    mini-css-extract-plugin \
    terser-webpack-plugin \
    optimize-css-assets-webpack-plugin \
    html-webpack-plugin \
    babel-loader @babel/core \
    vue-loader vue-template-compiler babel-preset-vue \
    sass-loader node-sass \
    css-loader \
    style-loader \
    postcss-loader postcss-preset-env precss autoprefixer \
    file-loader url-loader \
    svg-sprite-loader \
    @babel/preset-env @babel/plugin-syntax-dynamic-import \
    element-ui \
    normalize.css
```

在 `packages.json` 的 `scripts: {}` 中添加：

```js
"scripts": {
    ...
    "build": "NODE_ENV=production webpack --config natureself/django/webapp/webpack.config.js",
    "serve": "webpack-dev-server --config natureself/django/webapp/webpack.config.js"
}
```

然后，运行 `npm run build` 即可打包所有资源（用于构建生产环境），`npm run serve` 则会启动一个 webpack-dev-server，提供文件服务。
在日常开发时，通常需要分别启动 Django server 和 webpack-dev-server：

```sh
./manage.py runserver
npm run serve
```

在 webpack-dev-server 启动的情况下，网页支持热更新（仅 webpack 管理的资源会触发热更新，Django 的网页模板文件不会自动刷新）。

# webapp.js

webapp 打包了一些常用的 js 插件、一些我们自己开发的模块和工具函数，生成一个入口文件（entry），文件名为 `webapp.[hash].js`，
后面简称 webapp.js。

在 settings.py 中添加以下配置：

```python
INSTALLED_APPS = [
    ...
    webpack_loader,
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': os.path.join(BUILD_DIR, 'webapp/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}
```

然后在网页中就可以通过以下方式引用了：

```djangohtml
{% load render_bundle from webpack_loader %}

<html>
    <head>
        <!-- 注入 webapp 的入口 css 文件（如果有的话） -->
        {% render_bundle 'webapp' 'css' %}
    </head>
    <body>
        <!-- 注入 webapp 的入口 js 文件 -->
        {% render_bundle 'webapp' 'js' %}
    </body>
</html>
```

webapp.js 将所有的东西“挂载” 到 `window.webapp` 上面，因此在 html 中的内嵌脚本也可以直接使用，例如：

```djangohtml
{% load render_bundle from webpack_loader %}

<html>
    <head>
        <!-- 注入 webapp 的入口 css 文件（如果有的话） -->
        {% render_bundle 'webapp' 'css' %}
    </head>
    <body>
        <!-- 注入 webapp 的入口 js 文件 -->
        {% render_bundle 'webapp' 'js' %}

        <!-- 注意，{{ xxx }} 会被 Django 模板替换，但是下面这个是要给 vue 用的，所以需要用 verbatim 包住 -->
        {% verbatim %}
        <div id="app"><span>{{ message }}</span></div>
        {% endverbatim %}
        <script>
        new webapp.Vue({
            el: '#app',
            data: {
                message: 'Hello, Natureself!',
            }
        })
        </script>
    </body>
</html>
```

webapp 具体包含了哪些内容，请阅读代码：`natureself/django/webapp/web/index.js`。

# 定制 entry

对于简单的网页，webapp.js 可能够用，但是对于一个网站来说，往往需要更多定制的脚本（以及 css 等）。

我们约定，**每一个 Django app 中需要 webpack 处理的文件都放在 web/ 子目录中**。当网站需要定制 entry 时，
可以添加 `web/index.js` ，然后创建配置文件 `nsproject/webapp.js`，内容如下：

```js
module.exports = {
  // entry 会直接传递给 webpack，context 目录为 Django 项目的根目录。注意自定义的入口文件名不要叫 webapp，以免冲突
  entry: {
    mysite: 'mysite/web/index.js',
  },

  // 如果在自定义的 mysite.js 之外仍然需要使用 webapp.js，则设置 buildWebappEntry 为 true
  buildWebappEntry: false,
}
```

在 mysite.js 中，可以 `import` webapp 项目中提供的所有内容，我们已经在 webpack.config.js 中添加了一个 `@webapp` 的别名，
例如，如果我们想要使用 webapp 中的 `request.js`，可以这样添加：

```js
import request from '@webapp/request.js'
```

在日常开发中，一些会在许多项目中可以复用的东西，我们都要考虑能否提炼出来放到 webapp 中。

# 定制 webpack.config.js

在极少数的情况下，我们希望对 webapp 提供的 webpack.config.js 文件进行一些小的修改，这可以通过 `webpack-merge` 来实现，
请参考 `natureself/django/admin/webpack.config.js`。

# 如何使用图标

我们鼓励使用 svg 图标。具体教程可以参考：https://juejin.im/post/59bb864b5188257e7a427c09

推荐从 [iconfont](https://www.iconfont.cn/) 上找 svg 图标使用，也可以让设计师绘制 svg 图标。

对于可以复用的图标，我们都会放在 webapp 中，但是一些项目如果需要使用自定义的图标，可以放在自己应用目录中。
由于 svg 图片需要经过 webpack 处理，因此对于图标文件存放的路径有一定的要求。

svg 文件必须存放在 `icons/svg/` 目录下，具体可以查看 webpack.config.js 中 `svg-sprite-loader` 里面 `include` 字段的正则式。

然后，在项目中，还需要添加以下代码（例如可以在 `icons/index.js` 中）：

```js
import icons from '@webapp/icons'

const req = require.context('./svg', false, /\.svg$/)
icons.importAll(req)
```

# webapp 内容索引

## icons

提供了一个 Vue 组件 `<svg-icon>`，用法如下：

```html
<svg-icon name="user"/>
```

添加图标的方法见上文「如何使用图标」一节。

## requests

`requests` 是经过简单封装的 axios 的 client，它进行了如下处理：

* 对于需要 csrftoken 的请求，自动加上 `X-CSRFToken` Header
* 所有请求的返回都认为成功，不进入失败分支（即总是使用 `request({...}).then(response => {...})`，不使用 `catch()` 分支

`requests` 适合用于发起 API 请求。
