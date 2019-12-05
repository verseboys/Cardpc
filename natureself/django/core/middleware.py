from django.utils.functional import SimpleLazyObject

import json
import ipaddress

from .api import bad_request

def DecodeBodyJsonMiddleware(get_response):
    """
    这个中间件会检查请求的 Content-Type 是否为 json，如果是 json，则会尝试解析 body，并将解析后的内容
    保存到 request.json。如果 Content-Type 不是 json，那么 request.json 会设置为空字典，这主要是为了
    方便 view 函数中使用。如果 Content-Type 是 json、但 body 不是合法的 json，则会直接返回 400 。
    """
    def middleware(request):
        if 'json' not in request.META.get('CONTENT_TYPE', ''):
            request.json = {}
        else:
            try:
                request.json = json.loads(request.body)
            except json.JSONDecodeError:
                return bad_request('request body is not valid json')
        return get_response(request)
    return middleware

def VisitorLocationMiddleware(get_response):
    """
    判断请求是否来自内网，设置 request.visitor_location 。

    在我们的架构中，NSFE（nginx）会配置一个 X-Visitor-Location 的 http 头，并且保证用户无法伪造这个头。
    我们可以直接读取这个头。

    如果请求来自内网（例如在 k8s 中直接访问），则没有这个 http 头，我们直接判断用户的 IP，如果 IP 是
    私有地址，则认为该请求来自内网。
    """
    def get_visitor_location(request):
        visitor_location = request.META.get('HTTP_X_VISITOR_LOCATION')
        if not visitor_location:
            # if there is not 'X-Visitor-Location' header, the request comes from inner k8s
            remote_addr = request.META.get('REMOTE_ADDR')
            if ipaddress.ip_address(remote_addr).is_private:
                visitor_location = 'private'
            else:
                visitor_location = 'public'
        return visitor_location

    def middleware(request):
        request.visitor_location = SimpleLazyObject(lambda: get_visitor_location(request))
        return get_response(request)

    return middleware
