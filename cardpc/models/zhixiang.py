from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.functional import cached_property

import json
from model_utils import Choices

from natureself.django.core.utils import serialize_datetime

class ZhixiangExamination(models.Model):
    # 考试名称
    title = models.TextField(blank=False, verbose_name='名称')
    # 问卷星地址
    wjx_url = models.TextField(blank=True, default='', verbose_name='问卷星地址')
    # 要求必须完成的课程
    course = models.ForeignKey('course.Course', models.PROTECT, related_name='zhixiang_exams', verbose_name='课程')

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                title = self.title,
                wjx_url = self.wjx_url,
                course = self.course.serialize(),
                )

        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ZhixiangTraining(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE, related_name='zhixiang_training_data', verbose_name='用户')

    examination = models.ForeignKey('ZhixiangExamination', models.PROTECT, null=True, verbose_name='关联考试')

    A = Choices(
            (1, '未参与课程调研'),
            (2, '已参与课程调研'),
            )
    a_status = models.IntegerField(choices=A, verbose_name='课程调研状态', default=1)
    a_start = models.DateTimeField(null=True, verbose_name='课程调研开始时间')
    a_end = models.DateTimeField(null=True, verbose_name='课程调研结束时间')

    B = Choices(
            # 默认处于未学完课程的状态，代码中，当读取到状态为 1 时，应该重新根据实际情况计算用户是否已学完
            # 如果发现已学完，就写入数据库，以后就不用再次计算了
            (1, '未学完课程'),
            (2, '已学完课程'),
            )
    b_status = models.IntegerField(choices=B, verbose_name='培训课程状态', default=1)

    C = Choices(
            (1, '未参与资格认证'),
            (2, '已填写问卷星、等待审核'),
            (3, '审核通过'),
            (4, '审核未通过'),
            )
    c_status = models.IntegerField(choices=C, verbose_name='资格认证状态', default=1)
    c_start = models.DateTimeField(null=True, verbose_name='资格认证开始时间')
    c_end =  models.DateTimeField(null=True, verbose_name='资格认证结束时间')

    D = Choices(
            (1, '未参与考试'),
            (2, '已参与考试'),
            )
    d_status = models.IntegerField(choices=D, verbose_name='考试评定状态', default=1)
    d_start = models.DateTimeField(null=True, verbose_name='考试评定开始时间')
    d_end = models.DateTimeField(null=True, verbose_name='考试评定结束时间')

    def get_b(self):
        # 如果之前已经将状态标记为了已学完相应课程，那么就永远都是已学完
        if self.b_status == 2:
            return self.b_status

        # 2019.07.03 经过沟通，以下逻辑不再需要。课程学习状态与资质审核无关
        ## 如果没有通过资质审核，那么一定处于 b1
        #if not self.c3:
        #    return 1

        # 如果未关联考试，那么就没有相应的课程，
        if not self.examination:
            return 1

        # 否则，计算用户学习情况，如果计算结果为已学完，那么需要把 b_status 设置为 2 并保存入数据库
        course = self.examination.course
        course.fetch_presentationlesson_details(self.user)
        if course.all_presentationlessons_watched:
            self.b_status = 2
            self.save(update_fields=['b_status'])
            return 2
        return 1

    a = property(lambda self: self.a_status)
    a1 = property(lambda self: self.a == 1)
    a2 = property(lambda self: self.a == 2)

    b = cached_property(lambda self: self.get_b())
    b1 = property(lambda self: self.b == 1)
    b2 = property(lambda self: self.b == 2)

    c = property(lambda self: self.c_status)
    c1 = property(lambda self: self.c == 1)
    c2 = property(lambda self: self.c == 2)
    c3 = property(lambda self: self.c == 3)
    c4 = property(lambda self: self.c == 4)

    d = property(lambda self: self.d_status)
    d1 = property(lambda self: self.d == 1)
    d2 = property(lambda self: self.d == 2)

    def set_timestamp(self, field_name):
        # 设置 x_start, x_end 等时间戳字段，一次只能设置一个，会自动保存数据库
        # NOTE 这是一个内部函数，我们暂时不检查错误（比如传入了错误的 field_name）
        # NOTE 时间戳仅设置一次，如果一个时间戳已经有值了，就不在设置
        if not getattr(self, field_name):
            setattr(self, field_name, timezone.now())
            self.save(update_fields=[field_name])

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                user = self.user.serialize(),

                a_status = self.a_status,
                a_start = serialize_datetime(self.a_start),
                a_end = serialize_datetime(self.a_end),

                b_status = self.b,

                c_status = self.c_status,
                c_start = serialize_datetime(self.c_start),
                c_end = serialize_datetime(self.c_end),

                d_status = self.d_status,
                d_start = serialize_datetime(self.d_start),
                d_end = serialize_datetime(self.d_end),

                examination = self.examination.serialize() if self.examination else None,
                )

        return data if to_dict else json.dumps(data, ensure_ascii=False)

class ZhixiangNews(models.Model):
    """
    我们暂时先使用独立的知享新闻模块，等 CMS 开发好之后，再改为使用 CMS 页面
    """
    # 新闻标题
    title = models.TextField(verbose_name='新闻标题')
    # 新闻内容，富文本
    content = models.TextField(verbose_name='正文')
    # 新闻缩略图
    thumbnail = models.ForeignKey('media.Image', models.PROTECT, related_name='+', verbose_name='封面图片')
    # 新闻作者以及发布时间（显示在标题下方的信息）
    author_name = models.TextField(verbose_name='作者姓名')
    publish_time = models.DateTimeField(verbose_name='发布时间')

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                title = self.title,
                content = self.content,
                thumbnail = self.thumbnail.serialize(),
                author_name = self.author_name,
                publish_time = serialize_datetime(self.publish_time),
                )

        return data if to_dict else json.dumps(data, ensure_ascii=False)
