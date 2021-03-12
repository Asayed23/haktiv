from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from main.users.api import serializers
from main.users.models import User

class UserProfileModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)

    def get_serializer_class(self):
        serializer = serializers.UserProfileSerializer
        user = User.objects.get(email=self.request.user.email)
        fields = ("username", "first_name", "last_name", "avatar", "phone")
        if user.role == User.RESEARCHER or user.role == User.TRIAGER:
            fields = ("username", "first_name", "last_name", "avatar", "home_address", "phone", "bio")
        elif user.role == User.CUSTOMER:
            fields = ("username", "first_name", "last_name", "avatar", "company_name", "phone", "title")
        serializer.Meta.fields = fields
        return serializer

    def retrieve(self, request):
        serializer = self.get_serializer_class()
        return Response(serializer(instance=User.objects.get(pk=request.user.id)).data, status=status.HTTP_200_OK)
        
    def partial_update(self, request):
        instance = User.objects.get(pk=request.user.id)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


# class UserProfileAPIView(APIView):
#     premission_classes = (IsAuthenticated, )

#     def get(self, request, format=None):
#         print("Email Address: ", self.request.user.email)
#         user = User.objects.get(email=self.request.user.email)
#         fields = ("username", "first_name", "last_name", "avatar", "phone")
#         if user.role == User.RESEARCHER or user.role == User.TRIAGER:
#             fields = ("username", "first_name", "last_name", "avatar", "home_address", "phone", "bio")
#         elif user.role == User.CUSTOMER:
#             fields = ("username", "first_name", "last_name", "avatar", "company_name", "phone", "title")

#         serializer = serializers.UserProfileSerializer(instance=user, fields=fields)
#         return Response(serializer.data, status=status.HTTP_200_OK)