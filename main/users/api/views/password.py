from django.utils.translation import ugettext as _
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from main.core.api_base import APIResponseBase
from main.core.utils import reset_password_token, reset_password_request, is_email, change_user_password
from ...models import User
from ..serializers import UserResetPasswordRequestSerializer, UserResetPasswordConfirmSerializer, \
    ChangePasswordSerializer

class UserResetPasswordRequest(CreateAPIView, APIResponseBase):
    """
## User Reset Password Request
"""
    permission_classes = []
    serializer_class = UserResetPasswordRequestSerializer
    def post(self, request, *args, **kwargs):
        res_message, res_code = _("Unknown Error"), 400
        serializer = UserResetPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            try:
                user = User.objects.filter(email=email).get()
                res_message, res_code = reset_password_request(user=user)
                return self.success(code=res_code, message=res_message)
            except:
                pass
        return self.error(code=res_code, message=res_message)

class UserResetPasswordConfirm(ListCreateAPIView, APIResponseBase):
    """
Changing the password from the reset link

1. **GET**: `uidb64` , `token` <br>
    you have to send the new password via POST Method but with the same endpoint
	`400` ** with error message ** <br>

2. **POST**: `password`, `email` <br>
    `200` ** password changed ** <br>
	`400` ** with error message ** <br>
"""
    permission_classes = []
    serializer_class = UserResetPasswordConfirmSerializer
    def get(self, request, *args, **kwargs):
        res_message, res_code = _("Unknown Error"), 400
        required_fields = ["uidb64", "token"]
        if all(param in request.resolver_match.kwargs for param in required_fields):
            try:
                uid = force_text(urlsafe_base64_decode(request.resolver_match.kwargs["uidb64"]))
                user = User.objects.get(pk=uid)
                if reset_password_token.check_token(user, request.resolver_match.kwargs.get("token")):
                    return self.success(code=200, message=_("OK, You can set new password now"))
            except User.DoesNotExist:
                res_message = _("Error, User does not exist")
            except (TypeError, ValueError, OverflowError):
                pass
        return self.error(code=res_code, message=res_message)
    def post(self, request, *args, **kwargs):
        res_message, res_code = _("Unknown Error"), 400
        required_fields = ["uidb67", "token"]
        serializer = UserResetPasswordConfirmSerializer(data=request.data)
        if all(param in request.resolver_match.kwargs for param in required_fields) and \
            serializer.is_valid():
            email = request.data["email"]
            password = request.data["password"]
            try:
                uid = force_text(urlsafe_base64_decode(request.resolver_match.kwargs["uidb64"]))
                user = User.objects.get(pk=uid)
                if reset_password_token.check_token(user, request.resolver_match.kwargs["token"]) and \
                    is_email(email=email) and user.email == email:
                    res_message, res_code = change_user_password(user=user, password=password, request=request)
                    return self.success(code=res_code, message=res_message)
            except User.DoesNotExist:
                res_message = _("Error, User does not exist")
            except (TypeError, ValueError, OverflowError):
                pass
            return self.error(code=res_code, message=res_message)

class ChangePassword(CreateAPIView, APIResponseBase):
    """
Changing the password from Authenticated end point

1. **POST**: `password` <br>
    `200` ** password changed **<br>
    `400` ** with error message **<br>
    `403` ** can't change the password **<br>

**Note:** call is authenticated
"""
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    def post(self, request, *args, **kwargs):
        res_message, res_code = _("Unknown Error"), 400
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = request.data['old_password']
            password = request.data["password"]
            try:
                user = User.objects.get(pk=request.user.pk)
                if not user.check_password(old_password):
                    return self.error(code=401, message=_("Invalid Password, Old Password does not match"))
                res_message, res_code = change_user_password(user=user, password=password, request=request)
                return self.success(code=res_code, message=res_message)
            except User.DoesNotExist:
                pass
        return self.error(code=res_code, message=res_message)