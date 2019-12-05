from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db.models import Prefetch
from django.urls import reverse
from django.utils import timezone
from django.http import FileResponse

from natureself.django.core.shortcuts import render_for_ua
from natureself.django.course.models import Course, PresentationLesson
from natureself.django.account.decorators import role_required
from natureself.django.core import api
from natureself.admin.forms import Form, panels, choices
from natureself.admin.views import AdminView

from cardpc.models import User, ZhixiangNews, ZhixiangTraining, ZhixiangExamination
from cardpc.panels import UserSearchPanel

import xlsxwriter
import tempfile

ZX_SETTINGS = settings.ZHIXIANG

@require_http_methods(['GET'])
def homepage(request):
    """
    知享首页

    GET /zhixiang/

    除了新闻动态以外，其他数据全部 Hardcode 在页面中。
    """
    # TODO 需要确定首页新闻动态最多显示几条
    news = ZhixiangNews.objects.select_related('thumbnail').order_by('-publish_time')[:10]
    context = dict(news=news)
    return render_for_ua(request, 'cardpc/zhixiang/homepage.html', context=context)

@require_http_methods(['GET', 'POST'])
@login_required
def training(request):
    """
    知享呼吸培训认证相关页面（课程调研、培训课程、资格认证、考试评定）

    当使用 GET 请求时，渲染网页。用户在课程调研、资格认证、考试评定页面，
    可以点击「立即参加」按钮，此时需使用 API 的方式发送 POST 请求（注意，
    不是 form 的方式，必须是 API 的方式），POST 返回的 data 中有 redirect
    字段，该字段的值即为需要跳转的字段，前端可以直接跳转。

    POST /zhixiang/training/
    {
        action: 'start-a', // 取值：start-a, start-c, start-d
    }
    """
    status, _ = ZhixiangTraining.objects.select_related('examination').get_or_create(user=request.user)

    # 首先处理 POST 请求。我们只考虑正常情况，其他情况均返回 400 bad request
    if request.method == 'POST':
        action = request.json.get('action')
        if not action or action not in ('start-a', 'start-c', 'start-d'):
            return api.bad_request(message='缺少 action 参数或无效的 action')

        if action == 'start-a' and status.a1:
            status.set_timestamp('a_start')
            return api.ok(data=dict(
                redirect = ZX_SETTINGS['training']['investigation_wjx_url_pattern'] % request.user.id,
                ))
        elif action == 'start-c' and (status.c1 or status.c4):
            status.set_timestamp('c_start')
            return api.ok(data=dict(
                redirect = ZX_SETTINGS['training']['qualification_wjx_url_pattern'] % request.user.id,
                ))
        elif action == 'start-d' and status.b2 and status.d1:
            status.set_timestamp('d_start')
            return api.ok(data=dict(
                redirect = status.examination.wjx_url,
                ))

        # 所有其他情况，返回 400
        # 在前端展示合理的情况下，用户正常操作不应该触发其他情况
        return api.bad_request()

    # 接下来处理 GET 请求，我们需要准备每一个 tab 需要展示的文案信息
    """
    给前端提供的 context:
    {
        status: obj, // 这是 ZhixiangTraining 对象，正常情况下前端应该不需要使用

        default_tab: 'a', // 取值 a, b, c, d，表示默认显示哪一个 tab

        a: {
            status: 1, // 有两套文案，1 表示提示用户参与调研，2 为用户已参与调研后提示的内容
            // 两种状态的处理
            // 1. 用户未参加调研，显示介绍文案，以及「立即参加」按钮
            // 2. 用户已参加调研，文案提示已参与调研，无参加按钮
        },

        b: {
            courses: [course], // 课程列表
            // 其中，course 有这些有用的字段：
            // course.thumbnail.url: 课程缩略图
            // course.introduction: 课程介绍
            // course.lesson_url: 点击课程后需要跳转的地址
            status: 1, // 取值：1，2
            // 两种状态
            // 1. 用户点击课程时，提示请先参与课程调研
            // 2. 用户点击后进入课程页面
        },

        c: {
            status: 1, // 取值 1,2,3,4
            // 四种状态的处理：
            // 1. 未参加资格认证，显示介绍文案，以及「立即参加」按钮
            // 2. 已填表、待审核，文案提示已填表、等待审核，无参加按钮
            // 3. 已通过审核，文案提示已已审核通过，无参加按钮
            // 4. 审核被驳回，文案提示审核被驳回，可以重新填表，以及「立即参加」按钮
        },

        d: {
            status: 1, // 取值 1,2,3,4
            // 四种状态的处理：
            // 1. 未通过资质认证，文案提示请先通过资质认证，无参加按钮
            // 2. 已通过资质认证，未学习完课程，文案提示请先完成 xx 课程学习，无参加按钮
            // 3. 可以参加考试，显示「立即参加」按钮
            // 4. 已参与考试，文案提示等待官方公布结果
            course: obj, // 如果用户已经通过了资格认证，course 的值是其需要完成的课程，可以用于渲染文案
        },
    }
    """

    # (a1, *, *, *): 默认显示课程调研页
    # (a2, b2, c3, *): 默认显示考试页
    if status.a1:
        default_tab = 'a'
    elif status.a2 and status.b2 and status.c3:
        default_tab = 'd'
    else:
        default_tab = 'b'
    # 如果有 show 参数，则使用 show 参数
    show = request.GET.get('show')
    if show in ['a', 'b', 'c', 'd']:
        default_tab = show

    # 课程调研页状态（前端状态码正好等于后端 a 的值 ）
    # (a1, *, *, *): 显示「立即参加」按钮
    # (a2, *, *, *): 文案提示已参与调研，无按钮
    a_status = status.a

    # 培训课程页状态（前端状态码正好等于后端 a 的值）
    # (a1, *, *, *): 显示课程列表，点击课程时，弹窗提示：“参与调研后，才可参加培训！”
    # (a2, *, *, *): 显示课程列表
    b_status = status.a

    # 资格认证页状态（前端状态码正好等于后端 c 的值）
    # (*, *, C1, *): 显示「立即参加」按钮
    # (*, *, C2, *): 文案提示已填表，等待审核，不显示「立即参加」按钮
    # (*, *, C3, *): 文案提示已通过，不显示「立即参加」按钮
    # (*, *, C4, *): 文案提示审核被驳回，可以重新填表，显示「立即参加」按钮
    c_status = status.c

    # 考试评定页
    # (*, *, C1|C2|C4, *): 文案提示请先通过资格审核
    # (*, B1, C3, D1): 文案提示需要学习完某一个课程才能参加考试，请先学习
    # (*, B2, C3, D1): 可以参加考试，显示「立即参加」按钮
    # (*, *, *, D2)：文案提示已参加考试，等待官方公布考试结果，不显示「立即参加」按钮
    if status.c1 or status.c2 or status.c4:
        d_status = 1
    elif status.b1 and status.c3 and status.d1:
        d_status = 2
    elif status.b2 and status.c3 and status.d1:
        d_status = 3
    elif status.d2:
        d_status = 4

    exam_course = status.examination.course if status.examination else None

    courses = Course.objects \
            .filter(zhixiang_exams__isnull=False) \
            .select_related('thumbnail') \
            .distinct()
    courses = [course for course in courses if course.published]
    for course in courses:
        course.fetch_presentationlesson_details(request.user)
        course.lesson_url = reverse('zhixiang-lesson', kwargs=dict(id=course.default_presentationlesson.id))

    context = {
            'default_tab': default_tab,
            'a': { 'status': a_status, },
            'b': { 'status': b_status, 'courses': courses },
            'c': { 'status': c_status, },
            'd': { 'status': d_status, 'course': exam_course },
            }
    return render_for_ua(request, 'cardpc/zhixiang/training.html', context=context)

@require_http_methods(['GET'])
def wjx_callback(request, action):
    """
    用户在填写完问卷星表单后，问卷星会将浏览器重定向到这个页面

    GET /zhixiang/wjx/:action/?userid={userid}

    我们在处理完成后，将用户重定向到 training 页面

    这里不进行任何形式的报错，无论成功或是有错误，全都重定向到 training 页面
    """
    def redirect_to_training_page(default_tab=None):
        url = reverse('zhixiang-training')
        if default_tab:
            url = f'{url}?show={default_tab}'
        return api.redirect(url)

    userid = request.GET.get('userid')
    if not userid:
        return redirect_to_training_page()

    try:
        user = User.objects.get(id=userid)
    except User.DoesNotExist:
        return redirect_to_training_page()

    status = ZhixiangTraining.objects.filter(user=user).first()
    if not status:
        return redirect_to_training_page()

    default_tab = None
    if action == 'investigation':
        status.a_status = 2
        status.a_end = timezone.now()
        status.save(update_fields=['a_status', 'a_end'])
        default_tab = 'a'
    elif action == 'qualification':
        # TODO 还应该检查用户当前状态是否允许资格认证
        status.c_status = 2
        status.c_end = timezone.now()
        status.save(update_fields=['c_status', 'c_end'])
        default_tab = 'c'
    elif action == 'examination':
        # TODO 还应该检查用户当前状态是否允许考试
        status.d_status = 2
        status.d_end = timezone.now()
        status.save(update_fields=['d_status', 'd_end'])
        default_tab = 'd'

    return redirect_to_training_page(default_tab)

@login_required
@require_http_methods(['GET', 'POST'])
def lesson(request, id):
    """
    知享课程培训中的单节课页面

    可以使用 POST 请求发送观看计时以及标记已看到最后一页

    POST /zhixiang/lesson/<int:id>/
    {
        add_watch_time: 10,  // 添加10秒
        watch_end: true, // 可选参数，已观看到最后一页
    }

    回复：
    {
        // 是否标记为已学习，只有当请求中含有 watch_end，且最终状态为 watched，才为 true
        mark_watched: true/false,
        // 数据库中是否为已学习状态
        watched: true/false,
        // 用户累计学习的时长
        watched_seconds: 120,
    }
    """
    if request.method == 'POST':
        seconds = request.json.get('add_watch_time', 0)
        watch_end = request.json.get('watch_end', False)
        try:
            lesson = PresentationLesson.objects.select_related('presentation') \
                     .get(id=id, status=PresentationLesson.STATUSES.published)
        except PresentationLesson.DoesNotExist:
            return api.not_found()

        record = lesson.presentation.add_watch_time(request.user, seconds)
        mark_watched = False

        if watch_end:
            if record.watched_seconds > lesson.presentation.min_watch_seconds:
                record = lesson.presentation.mark_watched(request.user)
                mark_watched = True

        return api.ok(data=dict(
                mark_watched = mark_watched,
                watched = record.watched,
                watched_seconds = record.watched_seconds,
            ))

    try:
        lesson = PresentationLesson.objects \
                .filter(status=PresentationLesson.STATUSES.published) \
                .select_related('course', 'presentation') \
                .prefetch_related('presentation__slides') \
                .get(id=id)
    except PresentationLesson.DoesNotExist:
        return render_for_ua(request, 'cardpc/404.html', status=404)

    lesson.course.fetch_presentationlesson_details(request.user)
    lesson.record = lesson.presentation.get_watch_record(request.user)

    context = dict(
            lesson = lesson,
            course = lesson.course,
            course_lessons = lesson.course.presentationlessons,
            )
    return render_for_ua(request, 'cardpc/zhixiang/lesson.html', context=context)

@require_http_methods(['GET'])
def news_list(request):
    """
    知享新闻列表页

    注：由于目前设计图上没有分页，因此我们暂时先不实现分页，时间富裕的时候再实现

    GET /zhixiang/news/
    """
    all_news = ZhixiangNews.objects.select_related('thumbnail').all()
    context = dict(all_news=all_news)
    return render_for_ua(request, 'cardpc/zhixiang/news-list.html', context=context)

@require_http_methods(['GET'])
def news_detail(request, id):
    """
    知享新闻详情页

    GET /zhixiang/news/<int:id>/
    """
    try:
        news = ZhixiangNews.objects.select_related('thumbnail').get(id=id)
    except ZhixiangNews.DoesNotExist:
        return render_for_ua(request, 'cardpc/404.html', status=404)

    context = dict(news=news)
    return render_for_ua(request, 'cardpc/zhixiang/news-detail.html', context=context)

@method_decorator(role_required(['admin']), name='dispatch')
class NewsAdminView(AdminView):
    MODEL = ZhixiangNews
    ORDER_BY = ['-id']
    USE_PAGINATION = True
    QUERYSET_SELECT_RELATED = ['thumbnail']

    SEARCH_FORM = Form([
        panels.TextPanel('title', search_op='icontains'),
        panels.TextPanel('author_name', search_op='icontains'),
        panels.DateRangePanel('publish_time', form_field_name='publish_range'),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.TextPanel('title'),
        panels.TextPanel('author_name'),
        panels.ImageUploaderPanel('thumbnail', bucket='thumbnails'),
        panels.DateTimePickerPanel('publish_time'),
        panels.RichTextPanel('content'),
    ], model=MODEL, form_mode='edit')

@method_decorator(role_required(['admin']), name='dispatch')
class ExaminationAdminView(AdminView):
    MODEL = ZhixiangExamination
    QUERYSET_SELECT_RELATED = [
            'course',
            'course__owner',
            'course__thumbnail',
            'course__thumbnail__owner',
            ]

    EDIT_FORM = Form([
        panels.TextPanel('title'),
        panels.TextPanel('wjx_url'),
        panels.SelectPanel('course', choices=choices.ApiChoices('api-course-courses', label_field='title')),
    ], model=MODEL, form_mode='edit')

@method_decorator(role_required(['admin']), name='dispatch')
class TrainingAdminView(AdminView):
    MODEL = ZhixiangTraining
    QUERYSET_SELECT_RELATED = [
            'user',
            'examination',
            'examination__course',
            'examination__course__owner',
            'examination__course__thumbnail',
            'examination__course__thumbnail__owner',
            ]

    SEARCH_FORM = Form([
        UserSearchPanel('user', form_field_name='username'),
        panels.SelectPanel('a_status'),
        panels.SelectPanel('b_status'),
        panels.SelectPanel('c_status'),
        panels.SelectPanel('d_status'),
    ], model=MODEL, form_mode='search')

    EDIT_FORM = Form([
        panels.DividerPanel(title='课程调研'),
        panels.SelectPanel('a_status'),
        panels.DateTimePickerPanel('a_start', disabled=True),
        panels.DateTimePickerPanel('a_end', disabled=True),
        panels.DividerPanel(title='培训课程'),
        panels.DividerPanel(title='资格认证'),
        panels.SelectPanel('c_status'),
        panels.SelectPanel('examination', choices=choices.ApiChoices('api-zhixiang-examinations', label_field='title')),
        panels.DateTimePickerPanel('c_start', disabled=True),
        panels.DateTimePickerPanel('c_end', disabled=True),
        panels.DividerPanel(title='考试评定'),
        panels.SelectPanel('d_status'),
        panels.DateTimePickerPanel('d_start', disabled=True),
        panels.DateTimePickerPanel('d_end', disabled=True),
    ], model=MODEL, form_mode='edit')

    def patch_model(self, request, pk):
        model = super().patch_model(request,pk, no_save=True)
        model.save()

        if 'examination' in request.json:
            model.b_status = 1
            model.get_b()
            model.save()

        return api.ok(data=model)

@require_http_methods(['POST'])
@role_required(['admin'])
def api_export_training_data(request):
    xlsxfile = tempfile.NamedTemporaryFile(delete=False)
    workbook = xlsxwriter.Workbook(xlsxfile.name)
    worksheet = workbook.add_worksheet()

    for cell, title in [
            ('A1', '用户 ID'),
            ('B1', '用户名'),
            ('C1', '邮箱'),
            ('D1', '手机号'),
            ('E1', '课程调研状态'),
            ('F1', '需学习的课程'),
            ('G1', '课程学习状态'),
            ('H1', '资格认证状态'),
            ('I1', '需参加的考试'),
            ('J1', '考试评定状态'),
            ]:
        worksheet.write(cell, title)

    worksheet.set_column('B:H', width=20)
    worksheet.set_column('A:A', width=5)

    data = ZhixiangTraining.objects \
            .select_related('user', 'examination', 'examination__course') \
            .order_by('user_id') \
            .all()

    row = 1
    for record in data:
        # 课程学习状态是每一次访问时计算一次，这里强制计算一次，使得 record.b_status 得到正确的赋值
        record.get_b()
        worksheet.write(row, 0, record.user_id)
        worksheet.write(row, 1, record.user.username)
        worksheet.write(row, 2, record.user.email)
        worksheet.write(row, 3, record.user.phone)
        worksheet.write(row, 4, record.get_a_status_display())
        worksheet.write(row, 5, record.examination.title if record.examination else '-')
        worksheet.write(row, 6, record.get_b_status_display())
        worksheet.write(row, 7, record.get_c_status_display())
        worksheet.write(row, 8, record.examination.course.title if record.examination else '-')
        worksheet.write(row, 9, record.get_d_status_display())
        row += 1
    workbook.close()

    now = timezone.now().strftime('%Y%m%d%H%M%S')
    return FileResponse(open(xlsxfile.name, 'rb'), as_attachment=True, filename=f'培训信息导出{now}.xlsx')
