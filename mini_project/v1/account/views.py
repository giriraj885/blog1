from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from otslib.utils import helper
from rest_framework import serializers as rest_serializer
from base.views import BaseAPIView
from v1.account.serializers import ManageAccountSerializer
from base.authentication import CustomAuthentication

class ManageAccount(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)

    def post(self, request):
        print('post..')
        manage_user_serializer = ManageAccountSerializer(data=request.data)
        manage_user_serializer.is_valid(raise_exception=True)
        validated_data = manage_user_serializer.validated_data
        validated_data['user'] = request.user
        manage_user_serializer.save()
        response = helper.getPositiveResponse("Entry created successfully")
        return Response(response)


