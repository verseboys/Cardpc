from django.apps import AppConfig
from django.db import models
from django.core.exceptions import ImproperlyConfigured

def get_submodels(model, levels=None):
    """
    获取指定 model 的子类（Django multi-table inheritance 的子类）

    代码参考 django-model-utils 中的 _get_subclasses_recurse
    > https://github.com/jazzband/django-model-utils/blob/master/model_utils/managers.py
    """
    related_objects = [f for f in model._meta.get_fields() if isinstance(f, models.OneToOneRel)]
    rels = [
            rel for rel in related_objects
            if isinstance(rel.field, models.OneToOneField)
            and issubclass(rel.field.model, model)
            and model is not rel.field.model
            and rel.parent_link
            ]

    submodels = []
    if levels:
        levels -= 1
    for rel in rels:
        if levels or levels is None:
            for submodel in get_submodels(rel.field.model, levels=levels):
                submodels.append(submodel)
        submodels.append(rel.field.model)
    return submodels

class CardpcConfig(AppConfig):
    name = 'cardpc'

    def ready(self):
        from .models import ProjectPage

        # 注册所有页面类型，检查类型是否有重复
        TYPES = dict()

        # 用于检查页面名称是否有重复
        NAMES = dict()

        for model in get_submodels(ProjectPage):
            if not model.PAGE_NAME:
                raise ImproperlyConfigured(f'{model.__name__} 没有配置 PAGE_NAME')
            if model.PAGE_NAME in NAMES:
                raise ImproperlyConfigured(f'页面名称重复，相关model：{model.__name__}, {NAMES[model.PAGE_NAME].__name__}, 页面类型名称：{model.PAGE_NAME}')
            NAMES[model.PAGE_NAME] = model

            if not model.PAGE_TYPE:
                raise ImproperlyConfigured(f'{model.__name__} 没有配置 PAGE_TYPE')
            if model.PAGE_TYPE in TYPES:
                raise ImproperlyConfigured(f'页面类型名称重复，相关model：{model.__name__}, {TYPES[model.PAGE_TYPE].__name__}, 页面类型名称：{model.PAGE_TYPE}')

            TYPES[model.PAGE_TYPE] = model

        # 将页面类型挂载到 ProjectPage 上，方便以后直接访问
        ProjectPage.PAGE_TYPES = TYPES
