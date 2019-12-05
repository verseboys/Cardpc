"""
通用视频课程模块
"""
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property

from natureself.django.core.model_mixins import Orderable
from natureself.django.media.models import PresentationWatchRecord

import json
from model_utils import Choices

class Course(models.Model):
    """
    一个课程由若干 Lesson 组成
    """
    # 该课程的发布者
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, verbose_name='课程发布者')
    # 课程名称
    title = models.TextField(blank=False, verbose_name='课程名称')
    # 课程介绍，富文本内容
    introduction = models.TextField(verbose_name='课程介绍')
    # 课程缩略图
    thumbnail = models.ForeignKey('media.Image', models.SET_NULL, null=True, related_name='+', verbose_name='课程缩略图')

    def fetch_presentationlesson_details(self, user):
        """
        设置两个值：
        * self.presentationlessons: [PresentationLesson]
        * self.default_presentationlesson: 用户首个未学习过的课程
        * self.all_presentationlessons_watched: true/false
        """
        if hasattr(self, 'presentationlessons'):
            return
        self.presentationlessons = list(
                self.presentationlesson_set \
                        .filter(status=PresentationLesson.STATUSES.published) \
                        .select_related('presentation') \
                        .prefetch_related(models.Prefetch(
                            'presentation__watch_records',
                            queryset=PresentationWatchRecord.objects.filter(user=user, watched=True),
                        )) \
                        .order_by('id')
                )
        for lesson in self.presentationlessons:
            lesson.watched = len(lesson.presentation.watch_records.all()) > 0

        self.default_presentationlesson = self.presentationlessons[0] if self.presentationlessons else None
        for lesson in self.presentationlessons:
            if not lesson.watched:
                self.default_presentationlesson = lesson
                break

        self.all_presentationlessons_watched = all(
                [lesson.watched for lesson in self.presentationlessons]
                )

    @cached_property
    def published(self):
        # 如果课程下没有 published 状态的 lesson，则 published 为 false
        # 暂时只考虑 presentation_lesson
        return self.presentationlesson_set.filter(status=PresentationLesson.STATUSES.published).exists()

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                owner = dict(id=self.owner_id) if self.owner else None,
                title = self.title,
                introduction = self.introduction,
                thumbnail = self.thumbnail.serialize() if self.thumbnail else None,
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class Lesson(Orderable):
    class Meta:
        abstract = True

    # 该单节课所属的课程
    course = models.ForeignKey('Course', models.PROTECT, verbose_name='所属课程')
    # 单节课名称
    title = models.TextField(verbose_name='标题')
    # 单节课简介，富文本内容
    summary = models.TextField(verbose_name='简介')
    # 课程状态
    STATUSES = Choices(
            (1, 'published', '已发布'),
            (2, 'draft', '草稿'),
            )
    status = models.IntegerField(choices=STATUSES, default=STATUSES.draft, verbose_name='状态')
    # 课程附件
    attachments = models.ManyToManyField('media.Document', related_name='+', verbose_name='附件')

    # ---- 8< ----
    # 讲者信息
    # ---- 8< ----

    # 将来我们的数据库中需要有专门的讲者表，但每一个单节课都允许自定义 per-lesson 的信息
    # 所以这里会有一个 FK，但下面仍然有一些附加内容。
    # 在读取时，如果 per-lesson 但值为空，则尝试读取讲者表中的数据
    # TODO，现在暂时还没有讲者表
    #teacher = models.ForeignKey('Teacher', models.PROTECT)
    # 讲者姓名
    teacher_name = models.TextField(verbose_name='讲者姓名')
    # 讲者单位
    teacher_organization = models.TextField(verbose_name='讲者单位')
    # 讲者头像
    teacher_picture = models.ForeignKey('media.Image', models.PROTECT, verbose_name='讲者头像', null=True)
    # 讲者介绍，富文本
    teacher_introduction = models.TextField(verbose_name='讲者介绍')

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                course = self.course.serialize(),
                title = self.title,
                summary = self.summary,
                status = self.status,
                attachments = [att.serialize() for att in self.attachments.all()],
                teacher_name = self.teacher_name,
                teacher_organization = self.teacher_organization,
                teacher_introduction = self.teacher_introduction,
                teacher_picture = self.teacher_picture.serialize() if self.teacher_picture else None,
                sort_order = self.sort_order,
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class VideoLesson(Lesson):
    """
    表示视频单节课
    """
    # 该单节课所对应的视频
    video = models.ForeignKey('media.PolyvVideo', models.PROTECT, related_name='+')

    def serialize(self, to_dict=True):
        data = super().serialize()
        data['video'] = self.video.serialize()
        return data if to_dict else json.dumps(data, ensure_ascii=False)

class PresentationLesson(Lesson):
    """
    表示 PPT 单节课
    """
    # 该单节课所对应的 PPT
    presentation = models.ForeignKey('media.Presentation', models.PROTECT, related_name='+', verbose_name='PPT')

    def serialize(self, to_dict=True):
        data = super().serialize()
        data['presentation'] = self.presentation.serialize()
        return data if to_dict else json.dumps(data, ensure_ascii=False)
