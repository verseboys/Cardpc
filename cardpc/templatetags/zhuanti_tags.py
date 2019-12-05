from django import template

register = template.Library()


@register.inclusion_tag('cardpc/zhuanti/menu.html', takes_context=True)
def menu(context, parent, calling_page=None):
    menuitems = parent.get_children().live().in_menu()
    for menuitem in menuitems:
        menuitem.active = (calling_page.path.startswith(menuitem.path)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        'request': context['request'],
    }
