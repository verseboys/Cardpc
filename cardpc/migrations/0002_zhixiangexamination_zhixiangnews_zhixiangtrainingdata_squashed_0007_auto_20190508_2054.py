# Generated by Django 2.2.1 on 2019-05-08 12:54

import cardpc.models.user
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('cardpc', '0002_zhixiangexamination_zhixiangnews_zhixiangtrainingdata'), ('cardpc', '0003_auto_20190428_1629'), ('cardpc', '0004_auto_20190505_1508'), ('cardpc', '0005_auto_20190505_1756'), ('cardpc', '0006_auto_20190505_2112'), ('cardpc', '0007_auto_20190508_2054')]

    dependencies = [
        ('media', '0004_auto_20190425_1558'),
        ('media', '0005_auto_20190508_2054'),
        ('cardpc', '0001_initial'),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZhixiangExamination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(verbose_name='名称')),
                ('wjx_url', models.TextField(blank=True, default='', verbose_name='问卷星地址')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='zhixiang_exams', to='course.Course', verbose_name='课程')),
            ],
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', cardpc.models.user.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.CreateModel(
            name='ZhixiangNews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(verbose_name='新闻标题')),
                ('content', models.TextField(verbose_name='正文')),
                ('author_name', models.TextField(verbose_name='作者姓名')),
                ('publish_time', models.DateTimeField(verbose_name='发布时间')),
                ('thumbnail', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='media.Image', verbose_name='封面图片')),
            ],
        ),
        migrations.CreateModel(
            name='ZhixiangTrainingData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('investigation_status', models.IntegerField(choices=[(0, '未开始调研'), (1, '已开始调研、未收到问卷星回调'), (2, '已收到问卷星回调'), (3, '已人工确认'), (4, '已驳回')], default=0, verbose_name='状态')),
                ('investigation_started_at', models.DateTimeField(null=True, verbose_name='调研开始时间')),
                ('investigation_finished_at', models.DateTimeField(null=True, verbose_name='调研结束时间')),
                ('qualification_status', models.IntegerField(choices=[(0, '未开始调研'), (1, '已开始调研、未收到问卷星回调'), (2, '已收到问卷星回调'), (3, '已人工确认并通过'), (4, '已驳回')], default=0, verbose_name='状态')),
                ('qualification_started_at', models.DateTimeField(null=True, verbose_name='认证开始时间')),
                ('qualification_finished_at', models.DateTimeField(null=True, verbose_name='认证结束时间')),
                ('examination_status', models.IntegerField(choices=[(0, '未开始考试'), (1, '已开始考试，未收到问卷星通知'), (2, '已收到问卷星回调'), (3, '已人工确认并通过'), (4, '已驳回')], default=0, verbose_name='状态')),
                ('examination_started_at', models.DateTimeField(null=True, verbose_name='考试开始时间')),
                ('examination_finished_at', models.DateTimeField(null=True, verbose_name='考试结束时间')),
                ('examination', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cardpc.ZhixiangExamination', verbose_name='关联考试')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]