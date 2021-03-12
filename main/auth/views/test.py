from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from main.core.api_base import APIResponseBase
from main.users.backends import EnsureAuthenticated

class TokenTestView(APIView, APIResponseBase):
    permission_classes = (EnsureAuthenticated,)
    def get(self, request, *args, **kwargs):
        return self.success(code=200, message="OK", data=dict(is_verified=True))