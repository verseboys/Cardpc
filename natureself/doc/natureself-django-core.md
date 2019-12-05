这里提供在 Django 项目中常用的工具。

## `natureself.django.core.api`

`natureself.django.core.api` 提供了一系列函数，用于构造 API 响应。除个别特列外，所有 API 请求的响应均为 json 格式，内容如下：

```javascript
{
    // 以下三个属性为固定属性，即所有 response 中都会有这三个属性
    "code": 0,
    "message": "ok",
    "data": { ... },

    // 以下属性为可选属性，只在特定的 response 中会包含

    // 分页属性，当结果为资源列表且有分页时会包含该属性，此时，data 一般为数组类型
    "pagination": {
        "total": 123,     // 资源总数
        "page": 2,        // 当前页码（页码从1开始）
        "page_size": 10,  // 分页大小
        "last_page": 13,  // 最后一页的页码
        "from": 11,       // 当前页第一个资源的编号（从1开始）
        "to": 20,         // 当前页最后一个资源的编号（从1开始）
    },

    // 当发生内部错误（500）时，event_id 为 sentry 中的 event id
    "event_id": "xxxxxx",

    // POST、PUT、PATCH 等请求，如果请求提交的参数有误，结果中会包含 form_errors，描述错误信息，
    // form_errors 的格式是 Django 中 Form().errors() 的格式，具体请参考 Django 的文档
    "form_errors": {...},

    // 当未登录用户访问需要登录才可访问的资源时，返回 401，此时结果中包含 login_url，
    // 方便前端在必要时进行登录操作。该 URL 一般是网页的地址，可以直接跳转
    "login_url": "/account/login",
}
```

在我们早期的规范中，API Response 中会包含 `version` 属性，但根据这段时间的实践，`version` 并没有实际起作用，
反而在某些时候造成了误解。由于代码实现的原因，我们在服务端代码（以前的 `apiserver/responses.py`）中 hard code
为 `v2`，但有些 API 在设计时为第一版，因此 URL 中是 `/api/{service}/v1/...`，这给人带来了困惑。
早期设计 `version` 属性，是为了前端可以判断该响应的版本，从而可以作出相应的处理。
但实际上，我们在升级 API 时，不会不改变 URL，因此前端总是明确知道正在请求什么版本的 API，所以响应中的 `version`
就没有什么作用了。

关于 HTTP Status Code （后面简称 `status`）和 响应中的 `code` 的关系与区别。HTTP Status Code 一般由浏览器解析，
我们尽量让返回的 `status` 符合 HTTP 语义规范，**但我们的前端代码不应该通过判断 `status` 来判断 API 的结果是否正确**。
例如，虽然一般来说请求成功时会返回 200，但对于 *创建资源* 类的 API，`status` 可能为 201。

`code` 我们可以称之为业务状态码，在以前的规范文档中也叫 *应用错误码* 。前端的代码应该始终通过这个 code 来判断 API
的执行结果。一般来说，当请求被成功处理时，`code` 总是等于 0，但也可以有例外，例如有些请求成功之后，可能有多种不同的结果，
前端需要根据该结果来选择下一步要做的事情，此时 `code` 也可以不是 0，而是我们自定义的编码。当 API 请求发生错误时，
如果没有专门定义业务状态码，那么 `code` 默认等于 `status`。

以下是一些常用函数以及说明：

### `api.ok(message='ok', code=0, data=None, pagination=None)`

当 API 请求成功时，一般使用该函数构造 Response。通常来说，只需要提供 `data` 参数即可。对于一般的 CRUD 操作，
data 都是被操作对象在操作结束后数据库中最新值的序列化结果，对于 DELETE 操作，data 是删除前的值，LIST 操作 data
是该对象的数组。我们不鼓励修改 code 值，除非我们需要返回自定义业务状态码。

### `api.created(message='resource created', data=None)`

对于创建资源的请求，在创建成功后，使用该函数构造结果。

### `api.no_content()`

该函数在 API 请求中很少被使用。

### `api.bad_request(message='bad_request', code=400, form_errors=None, data=None)`

当请求由于客户端提供的数据有误而失败时，使用该函数构造响应。其中 message 建议设置为可以直接展示给用户查看的内容，
对于较复杂的情况，例如需要描述表单中哪些字段有问题，以辅助前端渲染错误提示，我们可以附上 `form_errors`。
一般来说不需要返回 `data`，因为没有任何对象被访问或操作。

### `api.not_authorized(message='not authorized', login_url=None)`

返回 401，前端应该提示用户登录。`login_url` 一般是登录的网页地址，前端可以直接跳转到相应页面。

### `api.forbidden(message='forbidden')`

返回 403，表示用户无权进行该操作。403 一般发生在用户已登录，但没有权限的情况。用户未登录时，一般返回 401。

### `api.not_found(message='not found')`

`GET`, `PUT`, `PATCH` 等操作的对象不存在时，应当返回 404 。

### `api.invalid_endpoint(message='invalid_endpoint')`

当请求一个不存在的 URL 时，返回这个结果。这个一般在全局配置。结果都是 404，通过 message 可以区分是地址有错误还是请求的资源不存在。
一般来说，在生产环境不会碰到该问题（后端 API 不会凭空消失）。

### `api.method_not_allowed(message='method not allowed')`

表示当前请求的方法不被允许。通常来说，返回 405 时，应该告知前端该 URL 允许使用哪些方法访问。
但是在我们开发的场景中，这个错误不会在生产环境发生，而在开发阶段，我们使用 API 时，总是应该对照文档，清楚支持哪些方法的。

### `api.internal_server_error(message='internal server error', event_id=None)`

当发生内部错误时，使用该函数构造响应。一般来说后端开发者无需调用该函数，我们会在项目全局配置。

### `not_implemented(message='not implemented')`

表示该 API 已经计划要实现，但现在还没有实现。在开发后端时，一般流程为：设计好 API，写上每个 API 的 view 函数，这些函数
在被正式实现前可以用该函数构造响应。这个错误不应该在生产环境出现（未实现的东西不应该被上线）。

### `redirect(location, permanent=False)`

返回 301（永久跳转） 或 302（暂时跳转） 跳转。301/302 的响应是支持有 body 的，但我们目前的场景中似乎并不需要，
所以暂时不支持设置 body，以后碰到实际需求时再说。

## `natureself.django.core.middleware`

目前主要有两个中间件，`DecodeBodyJsonMiddleware` 和 `VisitorLocationMiddleware`。

使用方法，在 `settings.py` 的 `MIDDLEWARE` 中加上：

```py
MIDDLEWARE = [
    ...
    'natureself.django.core.middleware.DecodeBodyJsonMiddleware',
    'natureself.django.core.middleware.VisitorLocationMiddleware',
]
```

### `DecodeBodyJsonMiddleware`

如果请求有 body （一般来说只有 `POST`、`PUT`、`PATCH` 等请求会有 body，但是RFC并不限制 `GET` 请求有 body，
实际上 elasticsearch 的一些 API 就会在 GET 请求中使用 body），并且 Content-Type 表明 body 是 JSON，
那么该中间件会将 body 按照 json 解析，然后保存到 `request.json`，在 view 的代码中可以直接使用，无需自行解析。
如果 Content-Type 不是 json 或者没有 body，则 `request.json` 会等于 `{}`，这里设置为 `{}` 而不是 `None`，
主要是方便 view 函数中使用，无需先判断 `request.json` 是否为空，可以直接当字典使用（当然请注意，body 解析出来后
有可能是数组而不是字典，虽然在我们合理的场景中功能还没有这样的现象）。

如果 Content-Type 表明内容是 json 格式，但是 body 不是合法的 json，那么该中间件会直接返回 400，view 函数不会被调用。

### `VisitorLocationMiddleware`

该中间件会设置一个 `request.visitor_location` 变量，变量值为 `public` 或 `private`，分别表示该请求来自公司内部
还是公网请求。这个中间件依赖我们的 Nginx 前端来设置 `X-Visitor-Location` 这个请求头，我们的 nginx 会保证用户无法
伪造这个头，即用户请求时自己写这个头，我们的 nginx 会擦除，改写成 public。

在本地开发时，由于没有 nginx，也就不会有这个头，因此直接判断 IP 地址是否为内网保留地址，如果是就返回 `private` 。
正常情况下，用户地址不会是内网保留地址，除非我们开发的系统是在某些组织内部使用（目前还没有）。

## `natureself.django.core.decorators`

目前有一个装饰器 `@private_network_required`，用于检查当前请求是否来自内网，一般用于管理后台 API，
或者内部各项目间互相调用的请求。早期实现这个，是为了简化权限验证。由于此前的项目都没有完善的API授权机制，
因此为了简化，我们使用访问者 IP 来控制权限。但以后我们的系统倾向于集成化，而不是为服务化，因此跨进程调用
的情况就很少，这种方式也就不再鼓励使用了。

这个装饰器依赖 `VisitorLocationMiddleware` 中间件才能工作。

## `natureself.django.core.utils`

目前提供了两个辅助函数，`get_pagination()`, `get_boolean_query()`. 详情请见函数的注释。

## `natureself.django.core.model_mixins`

目前提供了一个 `TimestampMixin` 以及一个 `CounterMixin` 的生成器。

`TimestampMixin` 会给 model 增加 `created_at` 和 `updated_at` 两个 field。

`AddCounter('read_count')` 会生成一个 `CounterMixin`，该 mixin 会给 model 增加一个 `read_count` field，
并且提供了一个 `inc_read_count()` 的累加函数（在数据库中执行，而不是 select-then-update）。

## `natureself.django.core.shortcuts`

目前提供了 `render_for_ua(request, template_name, *args, **kwargs)`，该函数用法与 `django.shortcuts.render` 是一样的，
区别是会根据当前的 UA 来自动查找使用的模板，如果当前 UA 是移动端，则会查找移动端的模板，如果不存在，会 fallback 到 PC 端。

## `natureself.django.core.templatetags.natureself`

提供了一些我们自己写的 template tag，目前主要是一些 SEO 或者站长工具类的东西。
