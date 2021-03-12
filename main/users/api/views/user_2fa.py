from django.utils.translation import ugettext as _
from rest_framework.viewsets import  ModelViewSet, GenericViewSet
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

from main.core.api_base import APIResponseBase
from main.core.utils import check_key_otp, create_qr_link
from ..serializers import UserSerializer, TwoFactorSerializer
from main.users.models import User

from qrcode import make as qrgen
from io import BytesIO
import base64

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

class TwoFactorView(ListCreateAPIView, APIResponseBase):
    """ Two Factor View"""
    permission_classes = (IsAuthenticated,)
    serializer_class = TwoFactorSerializer

    @swagger_auto_schema(query_serializer=serializer_class,)
    def get(self, request, *args, **kwargs):
        serializer = TwoFactorSerializer(data=request.data)
        if serializer.is_valid():
            otp = request.data["otp"]
            is_valid_otp = check_key_otp(key=request.user.key, otp=otp)
            if is_valid_otp:
                token = RefreshToken(user=request.user)
                return self.success(code=200, message=_("OK"),
                                    data=dict(token=token.access_token, refresh=token, is_valid=is_valid_otp))
            return self.error(code=403, message=_("Invalid OTP Code"))
        else:
            return self.invalid_serializer(serializer=serializer)

    def post(self, request, *args, **kwargs):
        """Set TwoFactor Authentication"""
        serializer = TwoFactorSerializer(data=request.data)
        if serializer.is_valid():
            otp = request.data["otp"]
            is_valid_otp = check_key_otp(key=request.user.otp_key, otp=otp)
            if is_valid_otp:
                user = request.user
                user.has_2fa = not user.has_2fa
                user.save()
                token = RefreshToken(user=request.user)
                return self.success(code=200, message=_("OK, 2 Factor Authentication has been set"),
                                    data=dict(token=token.access_token, refresh=token, has_2fa=user.has_2fa))
            return self.error(code=403, message=_("Invalid OTP Code"))
        else:
            return self.invalid_serializer(serializer=serializer)


class TwoFactorQRCodeView(ListAPIView, APIResponseBase):
    """ Get Two Factor QRCode"""
    permission_classes = (AllowAny,)
    serializer_class = TwoFactorSerializer

    @swagger_auto_schema(query_serializer=serializer_class, )
    def get(self, request, *args, **kwargs):
        serializer = TwoFactorSerializer(data=request.data)
        if serializer.is_valid():
            try:
                otp = request.data["otp"]
                link = create_qr_link(key=request.user.otp_key, user=request.user)
                img = qrgen(str(link))
                buffer = BytesIO()
                img.save(buffer)
                image_src = base64.b64encode(s=buffer.getvalue()).decode()
                response = f"data:image/png;base64,{image_src}"
                if request.user.has_2fa:
                    is_valid_otp = check_key_otp(key=request.user.otp_key, otp=(otp))
                    if is_valid_otp:
                        return self.success(code=200, message=_("OK"), data=dict(image_src=response))
                    else:
                        return self.error(code=400, message=_("Invalid OTP Code, please try again"))
                else:
                    return self.success(code=200, message=_("OK"), data=dict(image_src=image_src))
            except:
                pass
        else:
            return self.invalid_serializer(serializer=serializer)
        return self.error(code=400, message=_("Unknown Error"))