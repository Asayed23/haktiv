from django.utils.translation import ugettext as _
from django.db.models import Q

from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView

from main.core.api_base import APIResponseBase
from main.users.models import User, RegisteredUser
from ..serializers import  ResearcherRegistrationSerializer, CompanyRegistrationSerializer

from drf_yasg.utils import swagger_auto_schema


class ResearcherRegistrationView(CreateAPIView, APIResponseBase):
    permission_classes = [AllowAny]
    serializer_class = ResearcherRegistrationSerializer

    @swagger_auto_schema(
        operation_description=_("Researcher Registration"),
        request_body=serializer_class,
        responses={201: _("Researcher has been registered successfully"), 400: _("An error occurred")},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            data["email"] = data["email"].lower()

            if User.objects.filter(Q(username=data["email"])|Q(email=data["email"])).exists():
                return self.error(400, _("User account already exists"))
            if RegisteredUser.objects.filter(Q(email=data["email"])|Q(phone=data["phone"])).exists():
                return self.error(400, _("You have already submitted, we will inform you ASAP"))

            RegisteredUser.objects.create(
                email=data["email"],
                role=RegisteredUser.RESEARCHER,
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=data["password"],
                country=data["country"],
                phone=data["phone"],
                linkedin_profile=data["linkedin_profile"],
            )
            return self.success(201, _("You have submitted your registration successfully, "
                                       "we will inform you the registration result after review your registration"))
        else:
            return self.invalid_serializer(serializer)


class CompanyRegistrationView(CreateAPIView, APIResponseBase):
    permission_classes = [AllowAny]
    serializer_class = CompanyRegistrationSerializer

    @swagger_auto_schema(
        operation_description=_("Company Registration"),
        request_body=serializer_class,
        responses={201: _("Company has been registered successfully"), 400: _("An error occurred")},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            data["email"] = data["email"].lower()

            if User.objects.filter(Q(username=data["email"])|Q(email=data["email"])).exists():
                return self.error(400, _("User account already exists"))
            if RegisteredUser.objects.filter(Q(email=data["email"])|Q(phone=data["phone"])).exists():
                return self.error(400, _("You have already submitted, we will inform you ASAP"))

            RegisteredUser.objects.create(
                email=data["email"],
                company_name=data["company_name"],
                role_name=data["role_name"],
                role=RegisteredUser.CUSTOMER,
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=data["password"],
                country=data["country"],
                phone=data["phone"],
            )
            return self.success(201, _("You have submitted your registration successfully, "
                                       "we will inform you the registration result after review your registration"))
        else:
            return self.invalid_serializer(serializer)
