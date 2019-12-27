from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.views import APIView
from otslib.utils import helper
from rest_framework.parsers import FormParser, JSONParser
from rest_framework import serializers as rest_serializer
from rest_framework.serializers import ValidationError 
from base.views import BaseAPIView, get_response
from miniproject_user.models import User,BlackList,UserVerification
from miniproject_user.serializers import UserSignUpSerializer, UserSignInSerializer,UserProfileSerializer,UserPasswordUpdateSerializer,GetUserProfileSerializer,UserRemoveSerializer,ForgotpasswordSerializer,SetPasswordSerializer
from base.authentication import CustomAuthentication
# import logging

class SignUp(BaseAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user_signup_ser = UserSignUpSerializer(data=request.data)
        user_signup_ser.is_valid(raise_exception=True)
        user = user_signup_ser.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # logging.info('User registered successfully') 
        response = get_response('User registered.',BaseAPIView.PASS_RESPONSE_STATUS, BaseAPIView.SUCCESS_CODE, token)
        return Response(response)

class SignIn(BaseAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):      
        user_signin_ser = UserSignInSerializer(data=request.data)
        user_signin_ser.is_valid(raise_exception=True)
        validated_data = user_signin_ser.validated_data
        try:
            user = User.objects.get(phone=validated_data['mobile_number'])
        except:
            raise ValidationError('Mobile number or password is incorrect', code="002")

        if not user.check_password(validated_data['password']):
            raise ValidationError('Mobile number or password is incorrect') 

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        response = get_response('Valid user.',BaseAPIView.PASS_RESPONSE_STATUS,BaseAPIView.SUCCESS_CODE,token)
        return Response(response)
    
class UserProfileUpdate(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)
    # permission_classes = (AllowAny,)

    def get(self,request):
        user_profile_serializer = GetUserProfileSerializer(request.user)
        response = get_response("Retrieved profile", BaseAPIView.PASS_RESPONSE_STATUS,BaseAPIView.SUCCESS_CODE,user_profile_serializer.data)
        return Response(response)

    def put(self,request):
        # old_email = request.user.email
        user_profile_serializer = UserProfileSerializer(request.user, data=request.data)
        user_profile_serializer.is_valid(raise_exception=True)
        validated_data = user_profile_serializer.validated_data

        if user_profile_serializer.is_valid() == False:
            response = self.getErrorResponse(user_profile_serializer, status.HTTP_400_BAD_REQUEST)
            return Response(response, status=response['statusCode'])
        # validated_data['email'] = validated_data['email'].lower()
        user_profile_serializer.save()
        # if validated_data['email'] != old_email:
        #     jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        #     jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        #     payload = jwt_payload_handler(request.user)
        #     payload['user_id'] = str(payload['user_id'])
        #     token = jwt_encode_handler(payload)
        # else: 
        #     token = request.META['HTTP_AUTHORIZATION'][4:]

        response = get_response("Profile updated!",BaseAPIView.PASS_RESPONSE_STATUS, BaseAPIView.SUCCESS_CODE)
        return Response(response)

    def delete(self, request):
        try:
            user_remove_serializer = UserRemoveSerializer(data=request.data)
            if user_remove_serializer.is_valid() == False:
                response = self.getErrorResponse(user_remove_serializer, status.HTTP_400_BAD_REQUEST)
                return Response(response, status=response['statusCode'])
            validated_data = user_remove_serializer.validated_data

            user = User.objects.get(id=validated_data['user_id'])
            user.delete()
            response = get_response("User Deleted",BaseAPIView.PASS_RESPONSE_STATUS, BaseAPIView.SUCCESS_CODE,None)
        except User.DoesNotExist:
            response = get_response("User does not exist", BaseAPIView.FAIL_RESPONSE_STATUS, 400,None)
        return Response(response)

class Logout(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)

    def post(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION'][4:]
            black_list_token = BlackList(token=token)
            black_list_token.save()
            response = get_response("User logged out",BaseAPIView.PASS_RESPONSE_STATUS,BaseAPIView.SUCCESS_CODE,None)
        except Exception as e:
            raise ValidationError(e)
        return Response(response)


class ChangePassword(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)

    def put(self, request):     
        response = {}
        user = request.user
        passward_serializer = UserPasswordUpdateSerializer(data=request.data)
        passward_serializer.is_valid(raise_exception= True)          

        password_data = passward_serializer.validated_data
        if user.check_password(password_data['oldPassword']) == True:
            if password_data['password'] != password_data['passwordConfirmation']:
                raise ValidationError('Password and confirmpassword did not match')
            else:
                user.set_password(password_data['password'])
                user.save()
        else:
            raise ValidationError('Old password is not valid.') 
            
        response = get_response("Password updated!",BaseAPIView.PASS_RESPONSE_STATUS,BaseAPIView.SUCCESS_CODE,None)
        return Response(response)

class Forgotpassword(BaseAPIView):
    def post(self, request):
        forgot_password_serializer = ForgotpasswordSerializer(data=request.data)
        forgot_password_serializer.is_valid(raise_exception= True)
    
        validated_data = forgot_password_serializer.validated_data
        verification_token = helper.randomGeneratorCode()
        try:
            user_verification = UserVerification.objects.get(user=request.user)
            user_verification.verification_token = verification_token
            user_verification.save()
        except UserVerification.DoesNotExist:
            
            user_verification = UserVerification(
                verification_token = verification_token,
                user = request.user
            )
            user_verification.save()
        token = {
            'set_password_token':user_verification.verification_token
        }

        response = get_response('',BaseAPIView.PASS_RESPONSE_STATUS, BaseAPIView.SUCCESS_CODE, token)
        return Response(response)

class SetPassword(BaseAPIView):
    
    def post(self, request):
        set_password_serializer = SetPasswordSerializer(data=request.data)
        set_password_serializer.is_valid(raise_exception= True)

        validated_data = set_password_serializer.validated_data

        try:
            user_verification = UserVerification.objects.get(user=request.user, verification_token=validated_data['set_password_token'])
        except UserVerification.DoesNotExist:
            response = helper.getNegativeResponse("Invalid verification token", status.HTTP_400_BAD_REQUEST)

        user_verification.user.set_password(validated_data['password'])
        user_verification.user.save()
        response = get_response('Set password successfully',BaseAPIView.PASS_RESPONSE_STATUS, BaseAPIView.SUCCESS_CODE)
        return Response(response)

