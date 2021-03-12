from django.utils.translation import ugettext as _

from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response

from django.conf import settings

class APIResponseBase:
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,) if settings.DEBUG else (JSONRenderer,)

    def error(self, code=400, message=_("An error occured"), data=None):
        response = dict(
            data=data,
            code=int(code),
            message=str(message),
            error=True
        )
        return Response(data=response, status=code)

    def success(self, code=200, message=_("OK"), data=None, headers=None):
        response = dict(
            data=data,
            code=int(code),
            message=str(message),
            error=False
        )
        # if data and any((isinstance(data, dict), isinstance(data, list),)):
        #     response["data"] = data
        return Response(data=response, status=code, headers=headers)

    def invalid_serializer(self, serializer, message=_("Invalid inputs"), code=400):
        response = dict(
            data=serializer.errors,
            code=int(code),
            message=str(message),
            error=True
        )
        return Response(data=response, status=code)