from django.db import models
from django.db.models import F
from django.conf import settings
import inspect

def AddCounter(field_name):
    """
    Creates a CounterMixin, which adds a counter field to the child model, named as {field_name},
    and also adds an 'inc_{field_name}()' method for incrementing the value in a proper way.

    the 'inc_{field_name}()' method has following signature:

        def inc_counter(self, count=1, save=False):
            pass

    If 'save' is True, the model will be saved immediately, only the counter field is saved,
    any other fields, including 'updated_at' if present, won't be touched. It's reasonable
    not to update 'updated_at' when only updating the counter.
    """
    def inc_counter(self, count=1, save=False):
        setattr(self, field_name, F(field_name)+count)

        if save:
            self.save(update_fields=[field_name])

    inc_counter.__name__ = f'inc_{field_name}'

    attrs = {
            '__module__': 'natureself.django.core.model_mixins',
            'Meta': type('Meta', (), {'abstract': True}),
            field_name: models.IntegerField(default=0),
            inc_counter.__name__: inc_counter,
        }

    return type('CounterMixin', (models.Model,), attrs)

ReadCounterMixin = AddCounter('read_count')

# 在 medieco-next 这个项目中，在迁移数据时，需要设置 auto_now/auto_now_add 为 False，
# 以便将旧数据库中的这些时间迁移过来，但是在正常生产环境中，auto_now/auto_now_add
# 则应该设置为 True。因此，我们在 mediec-next 的 settings.py 中设置了这两个参数，
# 这里判断如果存在则使用，否则默认为 True。
_AUTO_NOW = getattr(settings, 'AUTO_NOW', True)
_AUTO_NOW_ADD = getattr(settings, 'AUTO_NOW_ADD', True)

class TimestampMixin(models.Model):
    """
    Adds 'created_at' and 'updated_at' to the child model.
    """
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=_AUTO_NOW_ADD)
    updated_at = models.DateTimeField(auto_now=_AUTO_NOW)

class Orderable(models.Model):
    """
    Orderable model, copied from wagtail (wagtail/core/models.py)
    """
    class Meta:
        abstract = True
        ordering = ['sort_order']

    sort_order = models.IntegerField(null=True, blank=True, editable=False)
    sort_order_field = 'sort_order'

def CreateVisitRecordModel(ModelName, field_name, model_name):
    """
    Creates a intermediate Model for ManyToManyField, which is used to track user access.
    It records the time of first visit, stored in 'visited_at'.

    It also ensures together_uniq with (user, field)
    """

    attrs = {
            '__module__': inspect.getmodule(inspect.stack()[1][0]).__name__,
            'Meta': type('Meta', (), {'unique_together': (('user', field_name),)}),
            field_name: models.ForeignKey(model_name, models.CASCADE, related_name='+'),
            'user': models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='+'),
            'visited_at': models.DateTimeField(auto_now_add=True),
            }

    return type(ModelName, (models.Model,), attrs)
