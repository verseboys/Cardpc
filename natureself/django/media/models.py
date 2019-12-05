from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from natureself.django.core.model_mixins import Orderable
from natureself.django.core.utils import serialize_datetime

import os
import json
import uuid
import magic
import pathlib
import hashlib
from model_utils import Choices

class FileManager(models.Manager):
    def create(self, bucket, file, **kwargs):
        """
        Create a file model, the given 'file' will be saved.

        'file': can be a string (an existing file path) or instance of UploadedFile
        'filename': optional (guess from 'file')
        'title': optional (default same to filename)
        'content_type': optional (guess from 'file')
        'key': optional (recommend not to set, will use uuid4() by default)
        'owner': optional (recommend always set a user)
        """
        if isinstance(file, UploadedFile):
            kwargs['filename'] = kwargs.get('filename') or file.name
            kwargs['size'] = file.size
            kwargs['content_type'] = kwargs.get('content_type') or file.content_type
        elif isinstance(file, str):
            if not os.path.exists(file):
                raise ValueError(f'File does not exist: {file}')
            kwargs['filename'] = kwargs.get('filename') or os.path.basename(file)
            kwargs['size'] = os.path.getsize(file)
            kwargs['content_type'] = kwargs.get('content_type') or magic.from_file(file, mime=True)
        else:
            raise ValueError(f'Bad type of "file": {type(file)}')

        kwargs['title'] = kwargs.get('title', kwargs['filename'])
        kwargs['bucket'] = bucket
        kwargs['key'] = kwargs.get('key') or uuid.uuid4().hex
        kwargs['local_path'] = self.model.gen_local_path(**kwargs)

        local_abs_path = os.path.join(settings.MEDIA_ROOT, self.model.STORAGE_ROOT, kwargs['bucket'], kwargs['local_path'])
        local_abs_dir = os.path.dirname(local_abs_path)
        if not os.path.isdir(local_abs_dir):
            pathlib.Path(local_abs_dir).mkdir(parents=True, exist_ok=True)

        md5 = hashlib.md5()
        if isinstance(file, UploadedFile):
            with open(local_abs_path, 'wb+') as out_fp:
                for chunk in file.chunks():
                    md5.update(chunk)
                    out_fp.write(chunk)
        elif isinstance(file, str):
            with open(local_abs_path, 'wb+') as out_fp, open(file, 'rb') as in_fp:
                for chunk in iter(lambda: in_fp.read(4096), b''):
                    md5.update(chunk)
                    out_fp.write(chunk)
        kwargs['md5sum'] = md5.hexdigest()

        return super().create(**kwargs)

class AbstractFile(models.Model):
    class Meta:
        abstract = True

    objects = FileManager()

    # 文件保存的路径: {MEDIA_ROOT}/{STORAGE_ROOT}/{bucket}/{key[:2]}/{key}
    # 访问地址为: {MEDIA_URL}/{STORAGE_ROOT}/{bucket}/{key[:2]}/{key}
    # 每一个继承的类都必须重新定义 STORAGE_ROOT，一般用类名的复数即可
    STORAGE_ROOT = 'files'

    # 文件属主，由于文件可能会在多处使用（比如发表的文章中），如果由于某种原因用户被删除，
    # 我们不应该删除相应的文件，文件都需要保留。
    owner = models.ForeignKey(get_user_model(), models.SET_NULL, null=True)

    # 文件标识，一般来说推荐使用 uuid4 随机生成，使用在文件的 URL 中，例如 /media/.../$key。
    # 我们不直接将文件名或者 model 的 id 暴露在 URL 中，如果是 id 暴露在 URL 中，会被人遍历下载，
    # 而文件名则常常会含有特殊字符，在前端渲染时容易处理不好。
    #
    # 我们并不将 key 设置为主键，因为使用字符串作为主键的性能很差，在不与 model 打交道的地方，
    # 我们仍然使用 model 的 id 来访问文件。
    #
    # 我们需要 Nginx 来配合，当用户请求 /media/.../$key 时，nginx 需要访问一下 django 后端，
    # 确定 1) 当前用户是否有权访问该文件 2) 获取文件名，用于生成 Content-Disposition 头
    key = models.TextField(unique=True)

    # 文件本地保存的路径，这里保存相对路径，相对的根为 settings.MEDIA_ROOT/self.STORAGE_ROOT/self.bucket/
    local_path = models.TextField()

    # 文件名，当用户下载文件时，会在 Content-Disposition 中加上 filename=$filename
    filename = models.TextField()

    # 有些使用场景中，需要给文件/图片一个标题
    title = models.TextField(blank=True)

    # 文件类型，默认为 application/octet-stream，后端会尽可能去检测该文件的类型，
    # 但并不保证检测出来的类型是正确的。
    content_type = models.TextField()

    # 文件大小（字节数）
    size = models.IntegerField()

    # 文件内容的 md5
    md5sum = models.TextField()

    # bucket 可以理解为一个子目录，一般来说我们鼓励按照用途来归类文件，每一种用途为一个 bucket，
    # 在将来，我们可能会按照不同的 bucket 来使用不同的存储后端
    bucket = models.TextField()

    # 软删除
    deleted_at = models.DateTimeField(null=True)

    @classmethod
    def gen_local_path(cls, **kwargs):
        key = kwargs.get('key')
        filename = kwargs.get('filename')
        ext = os.path.splitext(filename)[1]
        return f'{key[:2]}/{key}{ext}'

    def url(self, request=None, absolute_uri=False):
        url = os.path.join(settings.MEDIA_URL, self.STORAGE_ROOT, self.bucket, self.local_path)
        return url if (not request or not absolute_uri) else request.build_absolute_uri(url)

    def download_url(self, request=None, absolute_uri=False):
        return None

    @property
    def local_abs_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.STORAGE_ROOT, self.bucket, self.local_path)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def serialize(self, to_dict=True, request=None, absolute_uri=False):
        data = dict(
                id = self.id,
                owner = dict(id=self.owner_id),
                key = self.key,
                filename = self.filename,
                title = self.title,
                content_type = self.content_type,
                size = self.size,
                md5sum = self.md5sum,
                bucket = self.bucket,
                url = self.url(request, absolute_uri),
                download_url = self.download_url(request, absolute_uri),
                )

        return data if to_dict else json.dumps(data, ensure_ascii=False)

class Image(AbstractFile):
    STORAGE_ROOT = 'images'

    def download_url(self, request=None, absolute_uri=False):
        url = reverse('download-image', kwargs=dict(key=self.key))
        return url if (not request or not absolute_uri) else request.build_absolute_uri(url)

class Document(AbstractFile):
    STORAGE_ROOT = 'documents'

    def download_url(self, request=None, absolute_uri=False):
        url = reverse('download-document', kwargs=dict(key=self.key))
        return url if (not request or not absolute_uri) else request.build_absolute_uri(url)

class PolyvVideo(models.Model):
    """
    保利威视频
    """
    # 视频的属主，与 File 类似，如果用户由于某种原因被删除，视频也应该保留
    owner = models.ForeignKey(get_user_model(), models.SET_NULL, null=True)
    # 视频的标题
    title = models.TextField(blank=False, verbose_name='标题')
    # 保利威视频的 vid
    vid = models.TextField(blank=False, verbose_name='保利威 vid')
    # 视频长度
    duration = models.TextField(verbose_name='视频时长')
    # 缩略图
    thumbnail = models.ForeignKey('Image', models.PROTECT, verbose_name='缩略图')
    # 需要登录才可播放
    login_required = models.BooleanField(default=False, verbose_name='登录才可播放')

    # 观看过的用户
    watched_users = models.ManyToManyField(get_user_model(), through='PolyvVideoWatchRecord', related_name='+')

    def mark_watched(self, user):
        if user:
            PolyvVideoWatchRecord.objects.get_or_create(user=user, video=self)

    def get_watched(self, user):
        return user and self.watched_users.filter(pk=user.pk).exists()

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                owner = self.owner.serialize() if self.owner else None,
                title = self.title,
                vid = self.vid,
                duration = self.duration,
                thumbnail = self.thumbnail.serialize(),
                login_required = self.login_required,
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class PolyvVideoWatchRecord(models.Model):
    class Meta:
        unique_together = (
                ('user', 'video'),
                )
    video = models.ForeignKey('PolyvVideo', models.CASCADE, related_name='+')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='+')
    visited_at = models.DateTimeField(auto_now_add=True)

class PolyvLive(models.Model):
    """
    保利威直播
    """
    # 直播的属主
    owner = models.ForeignKey(get_user_model(), models.SET_NULL, null=True)
    # 直播但标题
    title = models.TextField(blank=False)
    # 保利威直播的 vid
    vid = models.TextField(blank=False)
    # 直播的缩略图
    thumbnail = models.ForeignKey('Image', models.PROTECT)
    # 直播（计划）开始/结束时间
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    # 可以强制标记该直播是否已开始/已结束
    STATUS_MARKS = Choices(
            (0, 'unset', '未设置'),
            (1, 'false', '标记为假'),
            (2, 'true', '标记为真'),
            )
    started = models.IntegerField(choices=STATUS_MARKS, default=STATUS_MARKS.unset)
    ended = models.BooleanField(choices=STATUS_MARKS, default=STATUS_MARKS.unset)
    # 回放视频
    playback = models.ForeignKey('PolyvVideo', models.SET_NULL, null=True)

    watched_users = models.ManyToManyField(get_user_model(), through='PolyvLiveWatchRecord', related_name='+')

    def mark_watched(self, user):
        if user:
            PolyvLiveWatchRecord.objects.get_or_create(user=user, live=self)

    def get_watched(self, user):
        return user and self.watched_users.filter(pk=user.pk).exists()

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                owner = self.owner.serialize() if self.owner else None,
                title = self.title,
                vid = self.vid,
                thumbnail = self.thumbnail.serialize(),
                start_at = serialize_datetime(self.start_at),
                end_at = serialize_datetime(self.end_at),
                started = self.started,
                ended = self.ended,
                playback = self.playback.serialize() if self.playback else None,
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class PolyvLiveWatchRecord(models.Model):
    class Meta:
        unique_together = (
                ('user', 'live'),
                )
    live = models.ForeignKey('PolyvLive', models.CASCADE, related_name='+')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='+')
    visited_at = models.DateTimeField(auto_now_add=True)

class Presentation(models.Model):
    """
    PPT
    """
    # PPT 的属主
    owner = models.ForeignKey(get_user_model(), models.SET_NULL, null=True)
    # PPT 的标题
    title = models.TextField(blank=False, verbose_name='标题')
    # PPT 的缩略图
    thumbnail = models.ForeignKey('Image', models.PROTECT, verbose_name='缩略图')
    # 最少观看时间，只有用户观看了超过这个时间，才能标记为已观看，若为0表示无限制
    min_watch_seconds = models.IntegerField(default=0, verbose_name='最少观看时间')

    watched_users = models.ManyToManyField(get_user_model(), through='PresentationWatchRecord', related_name='+')

    def mark_watched(self, user):
        if not user or not user.is_authenticated:
            return None

        record = self.get_watch_record(user)
        if record:
            record.watched = True
            record.save()
        else:
            record = PresentationWatchRecord.objects.create(user=user, presentation=self, watched=True)
        return record

    def add_watch_time(self, user, seconds):
        if not user or not user.is_authenticated:
            return None
        record = self.get_watch_record(user)
        if record:
            record.watched_seconds = models.F('watched_seconds') + seconds
            record.save()
            record.refresh_from_db()
        else:
            record = PresentationWatchRecord.objects.create(user=user, presentation=self, watched_seconds=seconds)
        return record

    def get_watch_record(self, user):
        return self.watch_records.filter(user=user).first()

    def get_watched(self, user):
        if not user:
            return False
        record = self.watch_records.filter(user=user).first()
        return record and record.watched

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                owner = self.owner.serialize(),
                title = self.title,
                thumbnail = self.thumbnail.serialize(),
                min_watch_seconds = self.min_watch_seconds,
                slides = [slide.serialize() for slide in self.slides.all()],
                )

        return data if to_dict else json.dumps(data, ensure_ascii=False)

class PresentationWatchRecord(models.Model):
    class Meta:
        unique_together = (
                ('user', 'presentation'),
                )
    presentation = models.ForeignKey('Presentation', models.CASCADE, related_name='watch_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='+')
    watched_seconds = models.IntegerField(default=0)
    watched = models.BooleanField(default=False)
    visited_at = models.DateTimeField(auto_now_add=True)

class Slide(Orderable, AbstractFile):
    """
    PPT 中的每一页图片
    """
    STORAGE_ROOT = 'slides'

    # 在后台管理中，先上传图片（不设置所属的PPT），在保存PPT时，再处理所有图片（以及排序）
    presentation = models.ForeignKey('Presentation', models.SET_NULL, null=True, related_name='slides')

    def serialize(self, to_dict=True, **kwargs):
        data = super().serialize(to_dict=True, **kwargs)
        data['sort_order'] = self.sort_order

        return data if to_dict else json.dumps(data, ensure_ascii=False)
