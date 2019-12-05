from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError

from natureself.django.otp.tools import verify_code, USAGES
from natureself.django.core.validators import is_valid_email, is_valid_phone

UserModel = get_user_model()

class BackendBase:
    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

class SmsCodeBackend(BackendBase):
    def authenticate(self, request, identity=None, phone=None, code=None, **kwargs):
        """
        短信验证码后端
        """
        if not phone and is_valid_phone(identity):
            phone = identity

        if not phone or not code:
            return None

        try:
            user = UserModel.objects.get(phone_validated=True, phone=phone)
        except UserModel.DoesNotExist:
            return None
        except FieldError:
            return None

        usage = kwargs.get('usage', USAGES.login)
        valid = verify_code('sms', request, phone, usage, code, True)

        if valid and self.user_can_authenticate(user):
            return user

class EmailCodeBackend(BackendBase):
    def authenticate(self, request, identity=None, email=None, code=None, **kwargs):
        if not email and is_valid_email(identity):
            email = identity

        if not email or not code:
            return None

        try:
            user = UserModel.objects.get(email_validated=True, email=email)
        except UserModel.DoesNotExist:
            return None
        except FieldError:
            return None

        usage = kwargs.get('usage', USAGES.login)
        valid = verify_code('email', request, email, usage, code, True)

        if valid and self.user_can_authenticate(user):
            return user
