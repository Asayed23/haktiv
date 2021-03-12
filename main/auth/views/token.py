from django.utils.translation import ugettext as _
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status

from main.core.api_base import APIResponseBase
from ..serializers import HaktivTokenObtainPairSerializer


class HaktivTokenView(TokenObtainPairView):
    """
        Haktiv Token
        User For Token Operations
    """

    serializer_class = HaktivTokenObtainPairSerializer

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #     except TokenError as e:
    #         raise InvalidToken(e.args[0])
    #     return self.success(code=status.HTTP_200_OK, message=_("OK"), data=serializer.validated_data)
    #     #return self.invalid_serializer(serializer=serializer)
