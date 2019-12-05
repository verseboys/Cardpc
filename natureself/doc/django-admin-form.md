# 表单系统

表单系统提供了一个定义表单的接口。在 Django 中，我们使用 Python 定义一个表单，
该表单定义可以被序列化为一个 JSON Schema，发送给前端，前端根据 JSON Schema 决
定如何渲染该表单。

表单主要有两种，搜索表单、编辑表单。其主要区别是，搜索表单中没有“必填”项，并
且所有项目的默认值均为 null。编辑表单则需要尊重后端的各种约束。

表单由两级元素组成，Form 和 Panel。Form 表示一个表单，即前端在发送请求时，
请求 body 中需要发送的内容均为 Form 的内容。Panel 表示表单中的一个 input，
对应请求 body 中的一个字段。

通常来说，一个 Form 会与一个 Model 绑定，一个 Panel 会与 Model 的一个 Field
绑定，但这并不是强制性要求。如果绑定了 Model，则有一些属性可以从 Model Field
中自动获取。

考虑到前端排版的需求，有一些 Panel 为非数据 Panel，即不参与数据交换，而仅仅
用于整合一些 Panel，便于前端组织表单项。

## json schema

### Form

```js
{
    // 表示该 json 是一个什么对象，这里总是 form
    object: 'form',

    // 取值有 'edit', 'search'，表示哪一种类型的 form
    form_mode: 'edit',

    // 该 Form 包含的 Panel
    panels: [ Panel, ... ],
}
```

### Panel

```js
{
    // 表示该 json 是一个什么对象，这里总是 panel
    object: 'panel',

    // 是否数据类型的 panel
    data_panel: true,

    // 表示这是一个什么类型的 Panel
    type: 'text',

    // 其所绑定的 Model 中 Field 的字段名，如果没有绑定 Field，则为 ''
    field_name: 'title',

    // 在表单数据中的字段名，通常与 field_name 相同，但有些情况下会有所不同，
    // 例如后端有一个字段叫 publish_time，表示文章发表的时间，而在搜索表单中，
    // 可能有一个字段叫 publish_range，用来搜索指定时间范围内的文章，此时：
    // field_name = 'publish_time', form_field_name = 'publish_range'
    form_field_name: 'title',

    // 有些 Field （主要是关系型字段，如 ForeignKey），后端返回给前端的数据
    // 是一个对象，而前端在提交数据时，应该提交该对象中的一个字段，例如有一个
    // 图片字段，前端在图片选择器中选择时，得到的是一个图片对象，在发送给服务器
    // 时，应该发送 'id' 的值，此时 form_field_property = 'id'
    form_field_property: null,

    // 是否是一对多或多对多的外部关系。如果是一对多或多对多，则表明，这里要保存的
    // 是一个数组，form_field_property 一般用 'id'
    many_field: false,

    // 该字段是否必填字段，在搜索表单中，所有字段都为非必填字段（用户单独指定的例外）
    required: false,

    // 是否允许修改，这比 edit_disallowed 更强，在新建、编辑模式下都不允许修改
    disabled: false,

    // 单独配置在 搜索、新建、编辑 表单中是否要禁用
    disabled_on_search: false,
    disabled_on_new: false,
    disabled_on_edit: false,

    // 在新建、编辑表单中是否隐藏
    hide_on_new: false,
    hide_on_edit: false,

    // 传递给输入控件（input widget）的一些配置信息。每一种类型的 Panel 可能有
    // 自己专有的配置项，这里列出一些公共的配置项
    options: {
        // input 的 label
        label: '文章标题',
        // 额外的帮助信息
        help_text: '显示在网页标签栏上的标题',
        // 默认值，渲染编辑时，如果后端没有提供该字段数据时的默认值
        default_value: null,
        // input 的 placeholder
        placeholder: null,
        // 对于 dropdown、select 等类型的控件，会有 choices 参数
        choices: {
            type: 'url',
            value_field: 'value',
            label_field: 'label',
            url: '/api/...',
            choices: [{ label: 'a', value: 'a' }, { label: 'b', value: 'b' }],
        },
    },

    // 给前端提供一些基本的数据校验规则，目前我们前端使用 element-ui，
    // element-ui 的表单使用 async-validators，我们在设计 validator 的时候需要考虑可实现性
    validators: [
        {},
    ]
}
```

非数据型 Panel：

```js
{
    object: 'panel',

    // 非数据型
    data_panel: false,

    // 如 inline, tab 等等
    // inline: 将几个表单项都渲染在同一行中
    // tab: 将渲染标签页
    type: 'inline',

    // 该 panel 所包含的 panel
    panels: [ Panel, ... ],

    // 标签型 Panel，包含每个标签的信息
    tabs: [
        { name: 'label1', panels: [ Panel, ...]] },
        { name: 'label2', panels: [ Panel, ...]] },
        ...
    ],
}
```
