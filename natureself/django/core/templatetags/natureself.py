from urllib.parse import urlencode
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def baidu_hm():
    """
    插入百度统计代码，官方文档见：https://tongji.baidu.com/web/help/article?id=174&type=0

    这将插入一段 <script> 标签，因此请在 <body> 的最后部分插入。
    """
    if settings.DEBUG or not getattr(settings, 'BAIDU_HM_ID'):
        return ''

    return mark_safe(f'''
<script>
var _hmt = _hmt || [];
(function() {{
  var hm = document.createElement("script");
  hm.src = "//hm.baidu.com/hm.js?{settings.BAIDU_HM_ID}";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
}})();
</script>
            ''')

@register.simple_tag
def sogou_site_verification():
    """
    插入搜狗站点验证代码，官方文档见：http://zhanzhang.sogou.com/index.php/help/siteVerify

    这将插入一段 <meta> 标签，因此请在 <head> 中插入。推荐使用 文件验证 的方式。
    """
    if settings.DEBUG or not getattr(settings, 'SOGOU_SITE_VERIFICATION_CONTENT'):
        return ''

    return mark_safe(f'<meta name="sogou-site-verification" content="{settings.SOGOU_SITE_VERIFICATION_CONTENT}" />')

@register.simple_tag
def qiho_site_verification():
    """
    插入360站点验证代码，官方文档见：http://www.so.com/help/help_3_8.html

    这将插入一段 <meta> 标签，因此请在 <head> 中插入。推荐使用 文件验证 或 CNAME验证 的方式。
    """
    if settings.DEBUG or not getattr(settings, 'QIHO_SITE_VERIFICATION_CONTENT'):
        return ''

    return mark_safe(f'<meta name="360-site-verification" content="{settings.QIHO_SITE_VERIFICATION_CONTENT}" />')

@register.simple_tag
def baidu_auto_push():
    """
    插入百度「自动推送」代码，官方文档见：https://ziyuan.baidu.com/college/articleinfo?id=267&page=2

    百度链接提交方式主要有几种：
    * 主动推送：后端通过 API 主动向百度提交新的链接
    * sitemap：后端生成 sitemap 文件，由百度定期抓取
    * 手工提交：手动登录百度后台提交链接
    * 自动推送：在网页中插入推送代码，当用户访问网页时，触发推送

    这将插入一段 <script> 标签，因此请在 <body> 末尾插入。建议使用主动推送的方式（hook 各类文章、视频发布的请求）。
    """

    if settings.DEBUG or not getattr(settings, 'ENABLE_BAIDU_PUSH'):
        return ''

    return mark_safe('''
<script>
(function(){
  var bp = document.createElement('script');
  var curProtocol = window.location.protocol.split(':')[0];
  if (curProtocol === 'https'){
    bp.src = 'https://zz.bdstatic.com/linksubmit/push.js';
  }
  else{
    bp.src = 'http://push.zhanzhang.baidu.com/push.js';
  }
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(bp, s);
})();
</script>
            ''')

@register.simple_tag
def qiho_auto_push():
    """
    插入360自动推送代码，未找到官方文档（相关文档可能需要登录后才可见）

    暂时不实现，如果后续需要，将找到官方文档后再决定如何处理。
    """
    return ''

@register.simple_tag
def cnzz_tracking():
    """
    插入 CNZZ 跟踪代码，未找到官方文档（相关文档可能需要登录后才可见）

    暂时不实现，如果后续需要，将找到官方文档以及与运营确认需求后再做处理。
    """
    return ''

# copied from https://stackoverflow.com/a/36288962/369018
@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)
