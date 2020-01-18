from rest_framework import generics, status, serializers
from miniproject_user.models import User
from base.serializers import BaseSerializer,BasePlainSerializer
from mini_project_serializer import miniproject_base_serializer
from v1.account.models import AccountManagement
from services.firebase import fb_service

class ManageAccountSerializer(BaseSerializer):
    price = miniproject_base_serializer.IntegerField(required=True, error_messages={
        'required': 'User type is required',
        'invalid' : 'Invalid user type'
    })

    current_time = miniproject_base_serializer.DateTimeField(required=True, error_messages={
        'required': 'Current time type is required',
        'invalid' : 'Invalid current time'
    })

    note = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter a note',
        'required_code' : 400,
        'blank': 'Note may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid note',
        'invalid_code' : 500
    })

    user_id =  miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter a user id',
        'required_code' : 400,
        'blank': 'User id may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid user id',
        'invalid_code' : 500
    })

    class Meta:
        model = AccountManagement
        fields = ('price','current_time','note','user_id')

    def create(self, validated_data):
        try:
            user = User.objects.get(id = validated_data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid user id')

        account_management = AccountManagement(
            price = validated_data['price'],
            current_time = validated_data['current_time'],
            note = validated_data['note'],
            credit_user = user,
            debit_user = validated_data['user']
        )
        account_management.save()
        message = "Hello"
        for token in user.fcm_token:
            fb_service.sendNotification(
                'New Message', 
                message,
                {   
                    'notification_type': 'chat', 
                    'last_timestamp': 'test',
                    'receiver_id' : user.id,
                    'sender_id' : validated_data['user'].id,
                    'user_name' : validated_data['user'].username,
                    'user_initial':'test'
                }, 
                token
            )
        return account_management
