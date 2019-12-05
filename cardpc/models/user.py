from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager

import json
import random
import string

class UserManager(DjangoUserManager):
    @classmethod
    def normalize_phone(cls, phone):
        phone = phone or ''
        return phone

    def generate_random_username(self):
        while True:
            username = 'cardpc_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
            if not self.filter(username=username).exists():
                return username

    def create_user(self, username=None, phone=None, email=None, **kwargs):
        # 参考 Django 的 BaseUserManager，对 username、phone 进行 normalize
        # 我们暂时不对手机号进行实质性的 normalize 操作，但将来也许会需要
        phone = self.normalize_phone(phone)

        if not username:
            username = self.generate_random_username()
        return super().create_user(username=username, phone=phone, email=email, **kwargs)

    def get_by_natural_key(self, username):
        try:
            return self.get(
                Q(username=username) |
                Q(phone_validated=True, phone=username) |
                Q(email_validated=True, email__iexact=username)
                )
        except self.model.MultipleObjectsReturned:
            # 在特殊情况下，有可能会选出多个用户，这会导致 Django 的 authenticate() 函数挂掉
            # 因此我们 Hack 一下，这种情况下抛出 DoesNotExist
            raise self.model.DoesNotExist()

class User(AbstractUser):
    """
    网站用户，普通会员、管理员均使用该 model

    需要在 settings.py 中设置：AUTH_USER_MODEL = 'cardpc.User'
    """
    objects = UserManager()

    # username, email, password, is_active, is_staff, is_superuser 在 AbstractUser 中定义

    # 手机号
    phone = models.TextField(blank=True)
    phone_validated = models.BooleanField(default=False)

    # 邮箱
    email = models.EmailField(blank=True)
    email_validated = models.BooleanField(default=False)

    # 用户注册的时间
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.username}'

    def serialize(self, to_dict=True):
        data = dict(
                id = self.id,
                username = self.username,
                email = self.email,
                email_validated = self.email_validated,
                phone = self.phone,
                phone_validated = self.phone_validated,
                )
        return data if to_dict else json.dumps(data, ensure_ascii=False)

    def set_phone(self, phone, save=True):
        update_fields = []
        if self.username == self.phone:
            self.username = phone
            update_fields.append('username')

        self.phone = phone
        update_fields.append('phone')

        if save:
            self.save(update_fields=update_fields)

    def set_email(self, email, save=True):
        update_fields = []
        if self.username == self.email:
            self.username = email
            update_fields.append('username')

        self.email = email
        update_fields.append('email')

        if save:
            self.save(update_fields=update_fields)
