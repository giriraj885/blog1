from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.views import APIView
from otslib.utils import helper
from django.db.models import Q
from base import constants
from rest_framework.parsers import FormParser, JSONParser,MultiPartParser,FileUploadParser
from rest_framework import serializers as rest_serializer
from rest_framework.serializers import ValidationError 
from base.views import BaseAPIView
from miniproject_user.models import User,BlackList,UserVerification
from miniproject_user.serializers import UserSignUpSerializer, UserSignInSerializer,UserProfileSerializer,UserPasswordUpdateSerializer,GetUserProfileSerializer,UserRemoveSerializer,ForgotpasswordSerializer,SetPasswordSerializer,GetUserListSerializer,FCMTokenSerializer,ProfilePhotoSerializer
from base.authentication import CustomAuthentication
from PIL import Image
from v1.account.models import AccountManagement
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
        response = helper.getPositiveResponse("User registered.", token)
        # response = get_response('User registered.',BaseAPIView.PASS_RESPONSE_STATUS, BaseAPIView.SUCCESS_CODE, token)
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
            response = helper.getNegativeResponse('Mobile number or password is incorrect')
            return Response(response, status=response['statusCode'])
            # raise ValidationError('Mobile number or password is incorrect', code="002")

        if not user.check_password(validated_data['password']):
            response = helper.getNegativeResponse('Mobile number or password is incorrect')
            return Response(response, status=response['statusCode'])
            # raise ValidationError('Mobile number or password is incorrect') 

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        response = helper.getPositiveResponse("Valid user.", token)
        # response = get_response('Valid user.',BaseAPIView.PASS_RESPONSE_STATUS,BaseAPIView.SUCCESS_CODE,token)
        return Response(response)
    
class UserProfileUpdate(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)
    # permission_classes = (AllowAny,)

    def get(self,request):
        user_profile_serializer = GetUserProfileSerializer(request.user)
        print(user_profile_serializer)
        response = helper.getPositiveResponse("Retrieved profile", user_profile_serializer.data)
        # response = get_response("Retrieved profile", BaseAPIView.PASS_RESPONSE_STATUS,BaseAPIView.SUCCESS_CODE,user_profile_serializer.data)
        return Response(response)

    def put(self,request):
        # old_email = request.user.email
        user_profile_serializer = UserProfileSerializer(request.user, data=request.data)
        user_profile_serializer.is_valid(raise_exception=True)
        validated_data = user_profile_serializer.validated_data

        if user_profile_serializer.is_valid() == False:
            response = helper.getNegativeResponse(user_profile_serializer)
            # response = self.getErrorResponse(user_profile_serializer, status.HTTP_400_BAD_REQUEST)
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

        response = helper.getPositiveResponse("Profile updated!")
        return Response(response)

    def delete(self, request):
        try:
            user_remove_serializer = UserRemoveSerializer(data=request.data)
            print(user_remove_serializer)
            user_remove_serializer.is_valid(raise_exception=True)
            validated_data = user_remove_serializer.validated_data

            user = User.objects.get(id=validated_data['user_id'])
            user.delete()
            response = helper.getPositiveResponse("User Deleted")
        except User.DoesNotExist:
            response = helper.getNegativeResponse("User does not exist")
        return Response(response)

class Logout(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)

    def post(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION'][4:]
            black_list_token = BlackList(token=token)
            black_list_token.save()
            if 'fcm_token' in request.data and request.data['fcm_token']:
                request.user.fcm_token.remove(request.data['fcm_token'])
                request.user.save()

            response = helper.getPositiveResponse("User logged out")
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
                response = helper.getNegativeResponse('Password and confirmpassword did not match')
                return Response(response, status=response['statusCode'])
                # raise ValidationError('Password and confirmpassword did not match')
            else:
                user.set_password(password_data['password'])
                user.save()
        else:
            response = helper.getNegativeResponse('Old password is not valid.')
            return Response(response, status=response['statusCode'])
            # raise ValidationError('Old password is not valid.') 
            
        response = helper.getPositiveResponse("Password updated!")
        return Response(response)

class Forgotpassword(BaseAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        forgot_password_serializer = ForgotpasswordSerializer(data=request.data)
        forgot_password_serializer.is_valid(raise_exception= True)
        
        validated_data = forgot_password_serializer.validated_data
        verification_token = helper.randomGeneratorCode()

        try:
            user = User.objects.get(phone=validated_data['mobile_number'])

            try:
                user_verification = UserVerification.objects.get(user=user)
                user_verification.verification_token = verification_token
                user_verification.save()
            except UserVerification.DoesNotExist:
                user_verification = UserVerification(
                    verification_token = verification_token,
                    user=user
                )
                user_verification.save()
        
            token = {
                'set_password_token':user_verification.verification_token
            }

            response = helper.getPositiveResponse('', token)
        except User.DoesNotExist:
            response = helper.getNegativeResponse("User does not exist")
        return Response(response)

class SetPassword(BaseAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        set_password_serializer = SetPasswordSerializer(data=request.data)
        set_password_serializer.is_valid(raise_exception= True)

        validated_data = set_password_serializer.validated_data

        try:
            user_verification = UserVerification.objects.get(verification_token=validated_data['set_password_token'])
        except UserVerification.DoesNotExist:
            response = helper.getNegativeResponse("Invalid verification token")
            return Response(response, status=response['statusCode'])

        user_verification.user.set_password(validated_data['password'])
        user_verification.user.save()
        response = helper.getPositiveResponse('Set password successfully')
        return Response(response)

class ManageUser(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)

    def get(self, request):
        user_per_page = constants.USER_PER_PAGE
        total_pages = 0
        page_start = 0
        page_end = user_per_page

        phone_list = []
        user_list = []
        phone_list.append(request.user.phone)

        user_list = User.objects.filter(
            ~Q(phone__in = phone_list)
        ).order_by('-updated_date_time')     

        if 'page_no' in request.GET and request.GET['page_no']!='0':
            page_end = int(request.GET['page_no']) * user_per_page
            page_start = page_end - user_per_page

            user_list_serializer = GetUserListSerializer(
            user_list[page_start:page_end], many=True,
            ) 
        else:
            user_list_serializer = GetUserListSerializer(
            user_list[page_start:page_end], many=True,
            ) 

        total_user = len(user_list)
        if total_user!=0:
            total_user_reminder = total_user%user_per_page
            total_pages = int(total_user/user_per_page)
            if total_user_reminder!=0:
                total_pages += 1

        response_data = {
            "total_pages" : total_pages,
            "total_user_count" : total_user,
            "user_list" : user_list_serializer.data,
            "items_per_page" : user_per_page
        }

        if len(response_data["user_list"]) == 0:
            response = helper.getPositiveResponse("No user found", response_data)
        else:    
            response = helper.getPositiveResponse("", response_data)
        return Response(response, status=response['statusCode'])

    def post(self, request):
        response = {}
        # try:   
        user = request.user
        fcm_serializer = FCMTokenSerializer(User.objects.get(id=user.id),data=request.data)
        if fcm_serializer.is_valid() == False:
            response = self.getErrorResponse(fcm_serializer, status.HTTP_400_BAD_REQUEST)
            return Response(response, status=response['statusCode'])

        fcm_serializer.save()
        response = helper.getPositiveResponse("")
        return Response(response, status=response['statusCode'])

class SaveProfilePhoto(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)
    parser_class = (FileUploadParser,)

    def post(self, request):
        if 'business_photo' not in request.data:
            response = helper.getNegativeResponse('business photo is require')
            return Response(response, status=response['statusCode'])
            # raise ParseError("Empty content")

        f = request.data['business_photo']

        try:
            img = Image.open(f)
            img.verify()
        except:
            response = helper.getNegativeResponse('Unsupported image type')
            return Response(response, status=response['statusCode'])
            # raise ParseError("Unsupported image type")
       
        request.user.profile_photo = f
        request.user.save()
        data = {'business_photo':request.user.profile_photo.url}
        response = helper.getPositiveResponse("Profile updated successfully",data)
        return Response(response, status=200)
        # try:
        #     print('request data..')
        #     print(request.data)
        #     profile_photo_serialzer = ProfilePhotoSerializer(request.user, data=request.data)
        #     print('in serializeer...')
        #     print(profile_photo_serialzer)
        #     if profile_photo_serialzer.is_valid() == False:
        #         response = self.getErrorResponse(profile_photo_serialzer, status.HTTP_400_BAD_REQUEST)
        #         return Response(response, status=response['statusCode'])
        #     user = profile_photo_serialzer.save()
        #     response = helper.getPositiveResponse("Profile updated successfully", user.profile.profile_photo.url)
        # except rest_serializer.ValidationError as exp:
        #     response = self.getValidationErrorMessage(exp.detail, status.HTTP_400_BAD_REQUEST)
        # except:
        #     response = helper.getNegativeResponse("Profile update failed", status.HTTP_500_INTERNAL_SERVER_ERROR)

        # return Response(response, status=response['statusCode'])

class GetAllUser(BaseAPIView):
    authentication_classes = (CustomAuthentication, JSONWebTokenAuthentication)

    def get(self, request):
        user_per_page = constants.USER_PER_PAGE
        total_pages = 0
        page_start = 0
        page_end = user_per_page
        user_list = []
        

        credit_user_list = AccountManagement.objects.filter(
            Q(credit_user=request.user),
            ~Q(debit_user=request.user)
        ).values_list('debit_user',flat=True).distinct('debit_user')

        debit_user_list = AccountManagement.objects.filter(
            ~Q(credit_user=request.user),
            Q(debit_user=request.user)
        ).values_list('credit_user',flat=True).distinct('credit_user')

        user_list = User.objects.filter(
            Q(id__in = credit_user_list)|
            Q(id__in = debit_user_list)
        )

        if 'page_no' in request.GET and request.GET['page_no']!='0':
            page_end = int(request.GET['page_no']) * user_per_page
            page_start = page_end - user_per_page

            user_list_serializer = GetUserListSerializer(
            user_list[page_start:page_end], many=True,
            ) 
        else:
            user_list_serializer = GetUserListSerializer(
            user_list[page_start:page_end], many=True,
            ) 

        total_user = len(user_list)
        if total_user!=0:
            total_user_reminder = total_user%user_per_page
            total_pages = int(total_user/user_per_page)
            if total_user_reminder!=0:
                total_pages += 1

        response_data = {
            "total_pages" : total_pages,
            "total_user_count" : total_user,
            "user_list" : user_list_serializer.data,
            "items_per_page" : user_per_page
        }

        if len(response_data["user_list"]) == 0:
            response = helper.getPositiveResponse("No user found", response_data)
        else:    
            response = helper.getPositiveResponse("", response_data)
        return Response(response, status=response['statusCode'])