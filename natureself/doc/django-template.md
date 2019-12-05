# 网站前端开发规范

## 关于 Vue

我们网站前端使用 Django 模板引擎来渲染，而相应的 js、css 文件则使用 webpack 打包。
网站前端不使用 SPA（Single Page Application）的原因主要是出于 SEO 方面的考虑，
在没有服务端渲染（SSR，Server Side Rendering）的情况下，不影响搜索引擎所以内容。

但是这并不意味着我们不能使用 Vue，在以下情况中，允许甚至鼓励使用 Vue：

* SEO 不敏感的页面，例如登录、注册页面
* 页面中非主要内容的局部组件

例如下面这个例子：

```html
<div id="app">
  <p>正文内容</p>
  <awesome-pagination />
</div>
```

在 js 脚本中：
```js
import AwesomePagination from './AwesomePagination.vue'

new Vue({
  el: '#app',
  components: {
    AwesomePagination,
  }
})
```

上述例子中，正文内容不通过 Vue 渲染，而是直接由 Django 渲染，那么即使搜索引擎内部没有 js 支持，
仍然可以读取到正文内容，不影响索引。而分页插件并非正文，可以额外实现 Single File Component，
通过 js 来动态加载。

## 文件路径规范

我们所有文件围绕 Django App 来组织，即一个文件如果属于某个 Django App 的功能，那么它应该放在
相应 Django App 的目录中。

以 [cardpc](https://git.evahealth.net/natureself/cardpc) 项目中 `cardpc/` 这个 app 为例：

* 所有 Django 模板放在 `templates/cardpc/` 中
* 所有 js 文件放在 `webapp/pages/` 中（例外情况单独讨论）
* 所有 css 文件放在 `webapp/styles/` 中

在日常的讨论中，我们可能会省略以上路径，请大家根据文件名自行推断文件是在哪一个目录中。

### 文件组织方式

在 Django 中，我们可能会有一些页面是相关的，例如「知享」相关的有一系列页面，
「专题」相关的有一系列页面，我们将这些页面用目录独立组织起来。

如果某个功能是孤立的、只有一个页面，那么它既可以是 `{module}.html`，也可以是 `{module}/index.html`，
例如 cardpc 中，登录、注册功能使用同一个 html 文件模板，相关功能模块名叫 `account`，
其模板文件名为 `account/index.html`。

css 文件一般与网页配套，即每一个网页有一个 css 文件，css 文件的路径建议与网页的路径保持一致。
如果某个模块数个网页共享同一个 css 文件并且也只需要这一个 css 文件，那么 css 文件名可以是
`{module}.scss`，也可以是 `{module}/index.scss`。

如果一个模块中有多个网页，网页之间有一些共享的 css 代码，可以在 `{module}/` 目录中放一个 `common.scss`，
然后在每个页面的 css 文件里 `@import "common.scss"` 。

js 文件与 css 文件的组织方式相同。如果一个页面需要多个 js 文件，那么可以再创建一层目录来组织这些文件，
例如 `account/index.html` 需要用到多个 js 文件（有一些是 Vue Single File Component），
可以放到 `account/*.vue`。

### 文件名

原则上，所有 js、css 文件的文件名全部小写，使用 kebab-case 的方式，不要用下划线，不要用 camelCase。
例如：

```
# Good
zhixiang-homepage.js

# Bad
loginReg.js
login_reg.js
```

所有 vue 文件，文件名使用 PascalCase （首字母也要大写）。例如：

```
# Good
ResetPassword.vue

# Bad
reset-password.vue
reset_password.vue
resetPassword.vue
```

### css 命名空间

由于所有 css 文件都会被打包到一起，全部加载。然而网页很大，如何避免冲突？
我们使用 dataset selector 来激活/区分。

我们在所有 html 的 `<body>` 标签上增加 `data-css` 属性，其值可以每一个页面单独设置。

`_base.html`：
```djangohtml
...
  <body data-css="{% block data-css %}{% endblock %}" >
  ...
  </body>
...
```
每一个继承 `_base.html` 的网页中，都可以这样提供自己的值：

`zhixiang/homepage.html`:
```djangohtml
{% extends 'cardpc/_base.html' %}

{% block data-css %}zhixiang zhixiang-homepage{% endblock %}
```

最终生成的网页是：

```html
<body data-css="zhixiang zhixiang-homepage">
...
</body>
```

在 css 文件中，可以这样去组织：

`zhixiang/index.scss`:
```css
[data-css~="zhixiang"] {
    // 所有 data-css 中含有 "zhixiang" 的部分，都会应用这个 block 里的东西
}
```

`zhixiang/homepage.scss`:
```css
[data-css~="zhixiang-homepage"] {
    // 所有 data-css 中含有 "zhixiang-homepage" 的部分，都会应用这个 block 里的东西
}
```

在上述例子中，`zhixiang/index.scss`、`zhixiang/homepage.scss` 这两个都见，都会作用于
`zhixiang/homepage.html` 这个页面的 `<body>` 上。

因此，我们约定，所有页面的 css 文件中，都用这个 `[data-css~="..."]` 来包住，
这样就可以有效的隔离，避免冲突了。

关于 dataset selector，可以看一下这篇文章：https://css-tricks.com/almanac/selectors/a/attribute/

这里简单罗列一下：

```css
[data-value] {
  /* Attribute exists */
}

[data-value="foo"] {
  /* Attribute has this exact value */
}

[data-value*="foo"] {
  /* Attribute value contains this value somewhere in it */
}

[data-value~="foo"] {
  /* Attribute has this value in a space-separated list somewhere */
}

[data-value^="foo"] {
  /* Attribute value starts with this */
}

[data-value|="foo"] {
  /* Attribute value starts with this in a dash-separated list */
}

[data-value$="foo"] {
  /* Attribute value ends with this */
}css
```

css 中，除了整页的控制，许多局部地区都可以使用这个技巧。

例如 `base.scss` 中，需要对 `_base.html` 中的 header, footer 应用样式属性，
而 `header`、`footer` 这类词过于普通，很容易有冲突，而 `_base.html` 又是所有网页的基础，
我们不能让 `base.scss` 应用到整个网页，因此，我们可以为 header, footer 分别设置添加属性：
`data-css="base-header"`、`data="base-footer"`，然后在 css 文件中就可以用这样的命名空间了：

```css
[data-css="base-header"] {
  ...
}
```

### js 文件加载方式

js 文件，我们使用类似 css 的方式，通过 `data-js` 这个属性来激活。除此之外，
我们还提供其他激活方式，下面逐一讲解。

以 cardpc 项目为例，在 `pages/index.js` 中有以下代码：

```js
import { activators, registerPageJs } from '@webapp/page.js'

registerPageJs(() => import('./partials/header.js'), activators.elementExists('.tab-menu'))
registerPageJs(() => import('./account/index.js'), activators.elementExists('#account-app'))
registerPageJs(() => import('./zhixiang/homepage.js'), activators.datajsContains('zhixiang-homepage'))
```

对于每一个 js 文件，我们都需要使用 `registerPageJs()` 来注册。这个函数有两个参数，一个是相应的文件(entry)，
另一个是激活规则（activator）。

大家注意到，所有 js 文件都使用这种方式加载：

```
() => import('./xxx.js')
```

这会告诉 webpack，相应的文件需要的动态加载，即只有用到的时候才会下载并加载。这里面的代码在执行时，
网页已经准备就绪，因此在 js 代码中无需再使用 `onReady()` 或类似的判断方式，可以直接开门见山的写代码。

而 activator 则比较灵活了，目前它支持传递三种东西：

* 正则式，例如 `/zhixiang/` ，那么，当当前网页 URL 可以被该正则式匹配时，相应的 js 就会被激活
* bool，即可以直接传递一个 bool 值进去，如果为 true，则相应的 js 就会被激活
* 函数，如果是函数的话，那么如果该函数执行的结果为真，相应的 js 就会被激活

例如，如果一个 js 文件希望在所有网页上都被激活，可以这样：

```
registerPageJs(() => import('./common.js'), true)
```

而函数就更加灵活了，我们可以执行更复杂的判断逻辑。在 `@webapp/page.js` 中，我们提供了几个预置的函数：

* `elementExists($selector)` 表示检查网页中是否存在某元素，如果存在，则激活。
例如 `partials/header.js` 文件主要是操作导航条。而导航条并不是所有页面上都有的（例如登录页面没有导航条），
因此我们希望这段 js 只有在发现页面里存在导航条元素时才被激活。导航条元素使用 `class="tab-menu"`，
因此 activator 可以用：`activators.elementExists('.tab-menu')`
* `datajsIs($value)` 表示 `data-js` 的值必须严格等于给定的值（与前面css 中的 `[data-value="foo"]` 一样）
* `datajsContains($value)` 表示 `data-js` 的值用空格隔开，其中有一项与给定的值相同（与前面 css 中的 `[datavalue~="foo"]` 一样）

虽然 css 的 dataset selector 还支持许多其他规则，但是我们约定应该只使用这两种情况，
否则 `data-js` 的值可能会过于复杂导致失控。

## 变量命名规范

js 中，我们统一使用 camelCase，与后端交互的过程中。后端吐出来的数据都是 snake\_case 的，
在直接使用后端数据的过程中，可以（也只能）使用 snake\_case 。但是，如果是在封装后端数据，
那么请使用 camelCase 。

举例说，在支持分页的 API 中，后端接受 `page_size` 参数，前端应该这样封装：

```js
function listFoo({ ..., pageSize = 10 } = {}) {
   let params = { ..., page_size: pageSize }
   return request({ ..., params })
}

// 在使用时：
listFoo({ ..., pageSize: 20 })
```

html 中，所有的 id、class 的值，全部使用 kebab-case。在特定情况下可以使用下划线（用来表达组件结构）。
但不允许使用大写字母（因此 camelCase、PascalCase 都不能使用）。
