这里提供文件、图片、保利威视频等封装的 Model。 `media` 对应 Django 中的 `MEDIA` 的概念，
与 `STATIC` 相对应，`STATIC` 可以看作是代码，是网站开发期间植入的数据，而 `MEDIA` 则是
网站运行期间上传的数据（可能是用户也可能是管理后台上传，总之不属于代码的一部分）。

我们曾经开发过 Storage Service（简称 ss），当时的背景是我们医咖会有多个端（Java 的管理后端、
django 的老后端），这两个后端需要共享上传的文件，为了避免重复开发，也为了部署时方便，
我们开发了 ss，同时，ss 隐藏了文件的实际存储后端。但在实践中发现，这个方法也显得有些麻烦，
因此我们重新开发了 `natureself.django.media`，调用者可以直接在本地调用，不需要跨进程调用，
使得调用变得更简单。同时，`natureself.django.media` 仍然可以实现隐藏文件实际存储后端的目的。

Django 本身提供了很好用的文件上传工具，包括：

* [FileField](https://docs.djangoproject.com/en/2.1/ref/models/fields/#filefield)
* [ImageField](https://docs.djangoproject.com/en/2.1/ref/models/fields/#imagefield)
* [Form](https://docs.djangoproject.com/en/2.1/topics/http/file-uploads/)

一般来说，直接使用 Django 的 `FileField` 和 `ImageField` 是最方便的。Django 会自行维护两个数据库表
来保存文件和图片信息。但我们希望可以在文件上保存更多的 meta 信息，并且将来可能会对 `Document`
实现访问权限控制等高级功能，也希望可以更方便的实现内容管理（类似 wagtail 中的 Image Galary
和 Document Galary），因此我们实现了 `natureself.django.media` 。

## 用法

在 model 中使用图片

```py
class SomeModel(models.Model):
    ...
    thumbnail = models.ForeignKey('media.Image', on_delete=models.PROTECT, related_name='+')
    ...
```

注意点：

* 需要在 `INSTALLED_APPS` 中加入 `natureself.django.media`
* `on_delete` 可以按需设置（例如设为 `SET_NULL`），在不清楚设置什么合适时，可以设置为 `PROTECT`
* `related_name` 最好设置为 `+` （即告诉 Django 不要建立反向关系），因为大多数时候没有用，并且有时候一个 model 可能会引用多个图片（例如医咖会中许多model都有 `thumbnail` 和 `mobile_thumbnail`两个字段引用图片，这种时候必须要将两个 `related_name` 设置为不同的内容，或者都设置为 `+`。

上传图片：

```py
image = Image.objects.create(bucket='thumbnails', file='/path/to/local/file')
some_model.thumbnail = image
```

注意点：

* `bucket` 可以简单理解为一层目录，例如 `thumbnails`, `avatars` 等，建议整个项目中统一规划若干 bucket，不要随意写。将来可能会按照bucket来调整存储后端。
* `file` 可以是一个本地存在的文件路径，也可以是 Django 的 `UploadedFile` 对象

目前医咖会项目中有这些 bucket：

* Image:
  * avatars, 保存用户头像
  * banners, 保存 Banner 图片
  * medals, 保存勋章图片
  * thumbnails, 保存各种缩略图（文章缩略图、视频缩略图等）
* Document:
  * attachments, 保存各种附件（图文教程附件、视频教程附件）

## 文件名

无论是图片还是文件，我们在本地保存的时候，都不直接用用户提供的原始文件名，而是会生成一个随机串
（目前使用 `uuid4()` 生成），使用该串作为文件名。文件的 URL 形如：

```
https://app.domain.com/media/document/attachments/fa/fa32dc55ce704e339ca6616c6e2e63d8.pdf
```

其中 `fa32dc55ce704e339ca6616c6e2e63d8` 就是随机生成的串。

这样设计的原因有：

* 用户可能会上传文件名相同的两个不同的文件，我们要能区分，并且保存时需要路径不同
* 用户上传的文件名可能含有一些特殊字符（比如空格、标点符号等），不利于运维管理（运维如果需要在命令行处理这些文件会很麻烦）
* 文件的 URL 中也不应该使用 `Image`/`Document` model 的 `id`，因为 `id` 是连续的，别有用意的用户可以遍历下载所有文件。
