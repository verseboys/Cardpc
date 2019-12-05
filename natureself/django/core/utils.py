from django.core.paginator import Paginator
from django.utils import timezone

def get_pagination(request, queryset, page=None, page_size=None):
    """
    根据 queryset 和 page/page_size 参数获取分页数据结构，返回三个东西：page, paginator, pagination

    * page: Django 中 paginator.get_page(page) 返回的对象，可以直接 iterate，为当前页的所有资源
    * paginator: Django 的 paginator，一般在调用者那里已经没什么用了
    * pagination: 格式化后的分页信息字典，可以直接在 api 响应中返回，pagination 的内容如下：

    {
        "total": 123,     // 资源总数
        "page": 2,        // 当前页码（页码从1开始）
        "page_size": 10,  // 分页大小
        "last_page": 13,  // 最后一页的页码
        "from": 11,       // 当前页第一个资源的编号（从1开始）
        "to": 20,         // 当前页最后一个资源的编号（从1开始）
    }

    参数:

    page/page_size: 如果调用时提供了 page/page_size 参数，则使用该参数，否则会尝试从 QueryString 中读取，即 request.GET.get('page')
    url: 一个函数，该函数接受 request 和 page(页码) 两个参数，可以生成指定页码的 URL，如果提供了该参数，
         那么在返回的 pagination 中还会有 current_url, next_url, previous_url 这三个参数。
    """
    if page is None:
        page = request.GET.get('page', 1)
    if page_size is None:
        page_size = request.GET.get('page_size', 10)

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page)
    pagination = {
        'total': paginator.count,
        'page': page.number,
        'page_size': page_size,
        'last_page': paginator.num_pages,
        'from': page.start_index(),
        'to': page.end_index(),
        # 兼容部分旧代码，以后需要删除这一段内容
        'pageSize': page_size,
        'lastPage': paginator.num_pages,
    }

    return page, paginator, pagination

def get_boolean_query(request, query, default=None):
    """
    获取一个 bool 类型的 querystring 参数。当该参数的值为 true, t, yes, y, 1 时（不区分大小写），返回 True，否则返回 False。

    如果 URL 中没有相应的 querystring，则返回 default。
    """
    value = request.GET.get(query, None)
    if value is None:
        return default
    return value.lower() in ('true', 't', 'yes', 'y', '1')

def get_datetime_query(request, query, format='%Y-%m-%d %H:%M:%S', default=None, raise_value_error=False,
        start_of_day=False, end_of_day=False):
    """
    获取一个 datetime 类型的 querystring 参数，返回 datetime 对象。

    如果 URL 中没有相应的 querystirng，则返回 default。

    如果 querystring 的值格式错误，则根据 raise_value_error 的值：
    * 若为 False，返回 default
    * 若为 True，则抛出异常
    """
    value = request.GET.get(query, None)
    return parse_datetime(value, format, default, raise_value_error, start_of_day, end_of_day)

def get_datetime_range_query(request, query, format='%Y-%m-%d %H:%M:%S', delim=',', default=None, raise_value_error=False, align_date=False):
    """
    获取一个时间区间的 querystring 参数，返回 (start, end) 对象。

    两个时间由 $delim 分割，如果某一个值不存在，则返回 default。format 为单个时间的格式。
    如果 align_date 为 True，则 start 的时间会改成 00:00 点，end 的时间会改成 23:59。

    例如：
    * 2019-04-20,2019-04-30，返回 (2019-04-20, 2019-04-30)
    * ,2019-04-30，返回 (None, 2019-04-30)
    """
    value = request.GET.get(query, None)
    if not value:
        start, end = default, default
    else:
        try:
            start, end = value.split(',')
        except ValueError as e:
            if raise_value_error:
                raise e
            else:
                start, end = default, default

    start = parse_datetime(start, format, default, raise_value_error, start_of_day=align_date)
    end = parse_datetime(end, format, default, raise_value_error, end_of_day=align_date)

    return start, end

def parse_datetime(value, format='%Y-%m-%d %H:%M:%S', default=None, raise_value_error=False, start_of_day=False, end_of_day=False):
    def replace_time(value):
        if value:
            if start_of_day:
                return value.replace(hour=0, minute=0, second=0)
            elif end_of_day:
                return value.replace(hour=23, minute=59, second=59)

        return value

    if value is None:
        value = default
    else:
        try:
            value = timezone.datetime.strptime(value, format)
            if timezone.is_naive(value):
                value = timezone.make_aware(value)
        except ValueError as e:
            if raise_value_error:
                raise e
            else:
                value = default

    return replace_time(value)

def serialize_datetime(t, format='%Y-%m-%d %H:%M:%S'):
    if not t:
        return None
    if timezone.is_aware(t):
        t = timezone.make_naive(t)
    return t.strftime(format)
