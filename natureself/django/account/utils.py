def get_user_roles(user):
    NS_ACCOUNT_ROLES_FIELD = getattr(user, 'NS_ACCOUNT_ROLES_FIELD', 'roles')

    # 如果用户 Model 已经实现了 roles 属性，则直接使用，否则使用默认的规则生成：
    # * 如果 is_staff 为 True，则表示用户是管理员（可以登录管理后台），roles 中包含 'admin'
    # * 如果 is_superuser 为 True，则表示用户是超级管理员，roles 中包含 'superuser'
    if hasattr(user, NS_ACCOUNT_ROLES_FIELD):
        return getattr(user, NS_ACCOUNT_ROLES_FIELD)
    else:
        roles = []
        if user.is_superuser:
            roles.append('superuser')
        if user.is_staff:
            roles.append('admin')
        return roles

def serialize_user(user):
    NS_ACCOUNT_SERIALIZE_METHOD = getattr(user, 'NS_ACCOUNT_SERIALIZE_METHOD', 'serialize')

    # 如果用户 Model 已经实现了 serialize() 方法，则直接使用，否则默认只序列化 username 和 email
    # 我们要求用户属性中必须包含 roles[] 字段，以供管理后台使用，因此如果用户 Model 自己实现了 serialize() 方法，
    # 那么建议该方法也序列化 roles 内容，否则这里会使用默认的方法计算角色。
    if hasattr(user, NS_ACCOUNT_SERIALIZE_METHOD):
        data = getattr(user, NS_ACCOUNT_SERIALIZE_METHOD)()
    else:
        data = dict(username=user.username)

    if 'roles' not in data:
        data['roles'] = get_user_roles(user)

    return data

def user_has_role(user, role):
    roles = get_user_roles(user)
    return role in roles
