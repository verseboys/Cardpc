from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from natureself.django.core.shortcuts import render_for_ua


@require_http_methods(['GET'])
def homepage(request):
    '''
    专题的首页，template_name为指定的模板名称，默认为default，
    '''
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/home.html')
    try:
        zhuanti = ZhuanTi.objects.get(id=id)
    except ZhuanTi.DoesNotExist:
        return render(request, '')

    # template_name 可以在专题的直接属性里面存在
    template_name = _get_template_by_zhuanti(zhuanti.slug)

    home_news = ZhuanTiNews.objects.all()[:10]
    # menus=Menu.objects.filter(tag=zhuanti.tag)
    menus = Menu.objects.all()
    footer = ''
    banner = ''
    summary = ''
    home_notices = ''
    home_videos = ''
    home_featurettes = ''
    context = dict(menus=menus,
                   footer=footer,
                   banner=banner,
                   news=home_news,
                   notices=home_notices,
                   videos=home_videos,
                   featurettes=home_featurettes,
                   )
    return render_for_ua(request, f'cardpc/zhuanti/{template_name}/homepage.html', context=context)


@require_http_methods(['GET'])
def news_list(request):
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/news-list.html')


@require_http_methods(['GET'])
def news_detail(request, id):
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/news-detail.html')


@require_http_methods(['GET'])
def video_list(request):
    '''
    视频和直播列表页
    '''
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/news-detail-2.html')


@require_http_methods(['GET'])
def video(request,id):
    '''
    视频播放页
    :param request:
    :return:
    '''
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/video.html')


@require_http_methods(['GET'])
def summary(request):
    '''
    会议简介页
    '''
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/summary.html')


@require_http_methods(['GET'])
def document_list(request):
    '''
    文件下载页
    '''
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/document-list.html')


@require_http_methods(['GET'])
def featurette_list(request):
    '''
    花絮
    '''
    template_name = _get_template_by_zhuanti('')
    return render(request, f'cardpc/zhuanti/{template_name}/featurette-list.html')


def _get_template_by_zhuanti(slug):
    '''
    预设：通用的按专题某属性获取模板名字
    :param slug:
    :return: default.  is reflected the path:  templates/cardpc/zhuanti/default
    '''
    return 'staticpage'
