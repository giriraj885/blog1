from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from otslib.utils import helper
from rest_framework import serializers as rest_serializer
from base.views import BaseAPIView
from v1.account.serializers import ManageAccountSerializer,GetCreditDetailSerializer,GetDebitDetailSerializer
from base.authentication import CustomAuthentication
from v1.account.models import AccountManagement
from base import constants
from django.db.models import Q

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

    def get(self, request):
        print('get method')
        records_per_page = constants.USER_PER_PAGE
        paginated_response = {
            "total_pages": 0,
            "total_records_count": 0,
            "records": [],
            "items_per_page": records_per_page
        }
        context = {'user': request.user}

        credit_user_list = AccountManagement.objects.filter(
            Q(credit_user=request.user) |
            Q(debit_user=request.user)
        )
        # debit_user_list = AccountManagement.objects.filter(debit_user=request.user)
        # print(debit_user_list)
        # if credit_user_list:
        print('in credit')
        paginated_response = self.get_paginated_records(request, credit_user_list)
        print(paginated_response)
        credit_debit_serializer = GetCreditDetailSerializer(paginated_response['records'],context=context, many=True)
        paginated_response['records'] = credit_debit_serializer.data
        paginated_response['items_per_page'] = records_per_page
        response = helper.getPositiveResponse('', paginated_response)
        return Response(response)

        # if debit_user_list:
        #     print('in debit')
        #     paginated_response = self.get_paginated_records(request, debit_user_list)
        #     print(paginated_response)
        #     credit_debit_serializer = GetDebitDetailSerializer(paginated_response['records'],context=context, many=True)
        #     print('in out...')
        #     print(paginated_response['records'])
        #     paginated_response['records'] = credit_debit_serializer.data
        #     paginated_response['items_per_page'] = records_per_page
        #     response = helper.getPositiveResponse('', paginated_response)
        #     return Response(response)

        # if credit_user_list.count() == 0:
        #     response = helper.getPositiveResponse('No Credit Found', paginated_response)
        #     return Response(response)

        # if debit_user_list.count() == 0:
        #     response = helper.getPositiveResponse('No Debit found', paginated_response)
        #     return Response(response)
