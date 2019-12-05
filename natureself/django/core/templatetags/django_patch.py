from django import template
from django.template.defaultfilters import stringfilter, Truncator

register = template.Library()

# Django 的简体中文翻译中，"String to return when truncating text" 漏了最后的“…”
# 临时修复这个 BUG 有几种方法：
# * 我们提供一个 locale 文件，覆盖 Django 的翻译
# * 使用这里 patch 过的 filter
# 由于我们之前没有 i18n 的经验，因此这里用 patch filter 的方法更简单、直观。
@register.filter(is_safe=True)
@stringfilter
def patched_truncatechars_html(value, arg):
    """
    Truncate HTML after `arg` number of chars.
    Preserve newlines in the HTML.
    """
    try:
        length = int(arg)
    except ValueError:  # invalid literal for int()
        return value  # Fail silently.
    return Truncator(value).chars(length, html=True, truncate='...')
