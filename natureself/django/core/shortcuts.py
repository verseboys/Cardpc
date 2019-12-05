from django.shortcuts import render as render

def render_for_ua(request, template_name, *args, **kwargs):
    """
    根据客户端UA来判断实际使用的模板名称。

    需要在 MIDDLEWARE 中启用 'django_user_agents.middleware.UserAgentMiddleware'

    假设模板名称是 'foo/bar.html'，对应的实际模板的文件名：
    * foo/bar.html         -- pc 端专用模板或自适配模板
    * foo/bar.mobile.html  -- 移动端专用模板

    如果当前 UA 是 PC 端，则按以下顺序搜索模板：
    * foo/bar.html
    * foo/bar.mobile.html

    如果当前 UA 是移动端，则按以下顺序搜索模板：
    * foo/bar.mobile.html
    * foo/bar.html
    """
    # 如果文件名不是 .html 结尾，我们暂时不做处理
    if not template_name.endswith('.html'):
        return render(request, template_name, *args, **kwargs)

    name_without_ext = template_name[:-5]

    if request.user_agent.is_mobile:
        template_name_list = [
                name_without_ext + '.mobile.html',
                name_without_ext + '.html',
                ]
    else:
        template_name_list = [
                name_without_ext + '.html',
                name_without_ext + '.mobile.html',
                ]

    return render(request, template_name_list, *args, **kwargs)
