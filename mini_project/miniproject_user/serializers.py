from rest_framework import serializers
from rest_framework.serializers import ValidationError
from miniproject_user.models import User, UserPermission,UserVerification
from base.views import randomGeneratorCode
from base.serializers import BaseSerializer,BasePlainSerializer
from mini_project_serializer import miniproject_base_serializer
from base import helper
import  time, datetime
import uuid
from datetime import timedelta

class UserSignInSerializer(BasePlainSerializer):
    mobile_number = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter your mobile number',
        'required_code' : 400,
        'blank': 'Mobile number can not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid mobile number',
        'invalid_code' : 500
    })
    password = miniproject_base_serializer.CharField(min_length=5, max_length=35, allow_blank=False, required=True, error_messages={
        'required': 'Please enter a password',
        'required_code' : 400,
        'blank': 'Password may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid password',
        'invalid_code' : 500
    })
            
class UserSignUpSerializer(BaseSerializer):
    mobile_number = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter your mobile number',
        'required_code' : 400,
        'blank': 'Your mobile number may not be blank',
        'blank_code' : 300
    })
    business_name = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter your business name',
        'required_code' : 400,
        'blank': 'Business name can not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid business name',
        'invalid_code' : 500
    })
    password = miniproject_base_serializer.CharField(min_length=5, max_length=35,required=True, error_messages={
        'required': 'Please enter a password',
        'required_code' : 400,
        'blank': 'Password may not be blank',
        'blank_code' : 300,
        'min_length' : "Password has at least 5 characters",
        'min_length_code' : 251,
        'max_length' : "Password has no more than 35 characters",
        'max_length_code' : 351,
    })
    passwordConfirmation = miniproject_base_serializer.CharField(min_length=5, max_length=35,required=True, error_messages={
        'required': 'Please enter a confirm password',
        'required_code' : 400,
        'blank': 'Password may not be blank',
        'blank_code' : 300,
        'min_length' : "Confirm password has at least 5 characters",
        'min_length_code' : 251,
        'max_length' : "Confirm password has no more than 35 characters",
        'max_length_code' : 351,
    })

    business_photo = miniproject_base_serializer.FileField(required=False,default='',allow_empty_file=True,error_messages={
        'invalid' : 'Invalid business photo',
        'invalid_code' : 500
    })

    # user_type = miniproject_base_serializer.IntegerField(required=True, error_messages={
    #     'required': 'User type is required',
    #     'invalid' : 'Invalid user type'
    # })

    business_address = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter your business address',
        'required_code' : 400,
        'blank': 'Business address can not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid business address',
        'invalid_code' : 500
    })

    class Meta:
        model = User
        fields = ('mobile_number','password','passwordConfirmation','business_name'
        ,'business_photo','business_address'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'passwordConfirmation' : {'write_only': True}
        }

    def create(self, validated_data):
        if User.objects.filter(phone=validated_data['mobile_number']).exists():
            raise ValidationError('User is aleary exist with this mobile number.', code="45")

        if validated_data['password'] != validated_data['passwordConfirmation']:
            raise ValidationError('Password and confirm password did not match', code="42")
        
        permissions = UserPermission(
            is_admin = False
        )
        permissions.save()

        user = User(
            phone = validated_data['mobile_number'],
            business_name = validated_data['business_name'],
            address = validated_data['business_address'],
            # user_type = validated_data['user_type'],
            permissions = permissions
        )
        user.set_password(validated_data['password'])
        
        user.save()

        if 'business_photo' in validated_data and validated_data['business_photo']:
            user.business_photo = validated_data['business_photo']
            user.save()

        return user


class UserProfileSerializer(BasePlainSerializer):    
    mobile_number = miniproject_base_serializer.IntegerField(required=False,default=0, error_messages={
        'invalid' : 'Invalid mobile number',
        'invalid_code' : 500
    })

    business_name = miniproject_base_serializer.CharField(required=False, allow_blank=True,default='', error_messages={
        # 'required': 'Please enter your business name',
        # 'required_code' : 400,
        # 'blank': 'Your business name may not be blank',
        # 'blank_code' : 300
         'invalid' : 'Invalid business name',
        'invalid_code' : 500
    })

    business_address = miniproject_base_serializer.CharField(required=False, allow_blank=True,default='', error_messages={
        # 'required' : 'Please address',
        # 'required_code' : 400,
        # 'blank': 'Address may not be blank',
        # 'blank_code' : 300
         'invalid' : 'Invalid business address',
        'invalid_code' : 500
    })

    name = miniproject_base_serializer.CharField(required=False, allow_blank=True,default='', error_messages={
        # 'required' : 'Please address',
        # 'required_code' : 400,
        # 'blank': 'Address may not be blank',
        # 'blank_code' : 300
        'invalid' : 'Invalid business address',
        'invalid_code' : 500
    })
     
    def update(self, instance, validated_data):
        user = instance
        
        if 'mobile_number' in validated_data and validated_data['mobile_number']:
            user_list = User.objects.filter(phone=validated_data['mobile_number']).exclude(phone=user.phone)
            if len(user_list) != 0:
                raise ValidationError('User is aleary exist with this mobile number.', code=450)
            user.phone = validated_data['mobile_number']
            
        if 'business_name' in validated_data and validated_data['business_name']:
            user.business_name = validated_data['business_name']

        if 'business_address' in validated_data and validated_data['business_address']:
            user.address = validated_data['business_address']

        if 'name' in validated_data and validated_data['name']:
            user.username = validated_data['name']
        
        user.save()
        return user

class GetUserProfileSerializer(BaseSerializer):
    userId = miniproject_base_serializer.CharField(source='get_user_id')
    mobile_number = miniproject_base_serializer.CharField(source='get_phone')
    business_address = miniproject_base_serializer.CharField(source='get_business_address')
    user_role = miniproject_base_serializer.CharField(source='get_user_role')

    class Meta:
        model = User
        fields = ('userId','mobile_number','photo','business_name','business_address','username','user_role')

class UserPasswordUpdateSerializer(BasePlainSerializer):
    oldPassword = miniproject_base_serializer.CharField(min_length=5, max_length=35,required=True,allow_blank=False, error_messages={
        'required': 'Old password required',
        'required_code' : 400,
        'blank': 'Old password may not be blank',
        'blank_code' : 300
        
    })
    password = miniproject_base_serializer.CharField(min_length=5, max_length=35,required=True,allow_blank=False, error_messages={
        'required': 'Password required',
        'required_code' : 400,
        'blank': 'Password may not be blank',
        'blank_code' : 300
    })
    passwordConfirmation = miniproject_base_serializer.CharField(min_length=5, max_length=35,required=True,allow_blank=False, error_messages={
        'required': 'Confirmation password required',
        'required_code' : 400,
        'blank': 'Confirmation password may not be blank',
        'blank_code' : 300
    })



class UserRemoveSerializer(BasePlainSerializer):
    user_id = miniproject_base_serializer.CharField(required=True,error_messages={
        'required': 'User id required.',
        'required_code' : 400,
        'invalid_choice': 'Invalid user id',
        'invalid_code' : 451,
        'blank': 'User id may not blank',
        'blank_code' : 300
    })

class ForgotpasswordSerializer(BasePlainSerializer):
    mobile_number = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter your mobile number',
        'required_code' : 400,
        'blank': 'Your mobile number may not be blank',
        'blank_code' : 300
    })
    
class SetPasswordSerializer(BasePlainSerializer):
    set_password_token = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Please enter your set password token',
        'required_code' : 400,
        'blank': 'Your set password token may not be blank',
        'blank_code' : 300
    })

    password = miniproject_base_serializer.CharField(min_length=5, max_length=35, allow_blank=False, required=True, error_messages={
        'required': 'Please enter a password',
        'required_code' : 400,
        'blank': 'Password may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid password',
        'invalid_code' : 500
    })

class GetUserListSerializer(BaseSerializer):
    userId = miniproject_base_serializer.CharField(source='get_user_id')
    mobile_number = miniproject_base_serializer.CharField(source='get_phone')
    business_address = miniproject_base_serializer.CharField(source='get_business_address')
    user_role = miniproject_base_serializer.CharField(source='get_user_role')
    business_photo = miniproject_base_serializer.CharField(source='get_business_photo')

    class Meta:
        model = User
        fields = ('userId','mobile_number','photo','business_name','business_address','username','user_type','user_role','business_photo')

class FCMTokenSerializer(BasePlainSerializer):
    fcm_token = miniproject_base_serializer.CharField(required=False, allow_blank=True,default='', error_messages={
        'invalid' : 'Invalid fcm token',
        'invalid_code' : 500
    })

    def update(self, instance, validated_data):
        user = instance
        fcm_token = validated_data['fcm_token']

        if fcm_token not in user.fcm_token:
            user.fcm_token.append(fcm_token)            
            user.save()
            
        return user

