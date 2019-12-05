"""
XXX Don't use, it's not well designed.
XXX see: https://github.com/yiminghe/async-validator, let's redesign Validator.
"""
class ValidatorBase:
    def __init__(self, message, trigger='blur', **kwargs):
        self.rule = dict(message=message, trigger=trigger)
        self.rule.update(kwargs)

    def serialize(self):
        return self.rule

class RequiredValidator(ValidatorBase):
    def __init__(self, message='必填', **kwargs):
        kwargs['required'] = True
        super().__init__(message=message, **kwargs)

class TextLengthValidator(ValidatorBase):
    def __init__(self, min=None, max=None, message=None, **kwargs):
        if min and not max:
            if not message:
                message = f'最少 {min} 个字符'
            kwargs['min'] = min

        elif not min and max:
            if not message:
                message = f'最多 {max} 个字符'
            kwargs['max'] = max

        elif min and max:
            if not message:
                message = f'长度在 {min} 和 {max} 个字符'
            kwargs['min'] = min
            kwargs['max'] = max
        else:
            raise ValueError('You must provide at least one of min and max')

        super().__init__(message=message, **kwargs)
