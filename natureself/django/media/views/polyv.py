from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model

from natureself.django.media.models import PolyvVideo
from natureself.django.account.utils import user_has_role

import json
import hashlib

SECRETKEY = settings.POLYV['SECRETKEY']
User = get_user_model()

# 保利威视频播放校验
# 文档：http://dev.polyv.net/2015/videoproduct/v-manual/v-manual-encrypt/jsgn0032/

class PolyvResponse:
    def __init__(self, request):
        self.vid = request.GET.get('vid', '')
        self.code = request.GET.get('code', '')
        self.t = request.GET.get('t', '')
        self.callback = request.GET.get('callback', None)

    def response(self, context):
        signstr = f'vid={self.vid}&secretkey={SECRETKEY}&username={context["username"]}&code={self.code}&status={context["status"]}&t={self.t}'
        sign = hashlib.md5(signstr.encode('utf8')).hexdigest().lower()
        context['sign'] = sign

        if self.callback:
            context = json.dumps(context)
            return HttpResponse(f'{self.callback}({context})', content_type='application/javascript; charset=utf-8')
        else:
            return JsonResponse(context)

    def ok(self, message, username):
        context = dict(
                status = 1,
                message = message,
                username = username,
                )
        return self.response(context)

    def reject(self, message, username=''):
        context = dict(
                status = 2,
                message = message,
                username = username,
                )
        return self.response(context)

def polyv_validate(request):
    video_id = request.GET.get('vid')

    try:
        video = PolyvVideo.objects.get(vid=video_id)
    except PolyvVideo.DoesNotExist:
        # 如果当前是在管理后台，运营输入新的 vid 之后可以自动预览，
        # 此时即使数据库中不存在此视频，也允许播放。
        # 目前我们暂时没有简单的方法判断用户是否来自管理后台，因此我们只判断用户是否为管理员
        if user_has_role(request.user, 'admin'):
            return PolyvResponse(request).ok(message='', username=request.user.username)
        return PolyvResponse(request).reject(message='视频不存在')

    if video.login_required and not request.user.is_authenticated:
        return PolyvResponse(request).reject(message='请登录后播放')

    return PolyvResponse(request).ok(message='', username=request.user.username)
