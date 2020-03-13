from rest_framework import generics, status, serializers
from miniproject_user.models import User
from base.serializers import BaseSerializer,BasePlainSerializer
from mini_project_serializer import miniproject_base_serializer
from v1.account.models import AccountManagement,BankDetails
from services.firebase import fb_service
from base import helper,constants
from django.db.models import Q, Count, Case, When, Avg, Sum, IntegerField,F
from django.db.models.functions import Coalesce

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
        message = validated_data['user'].business_name + ' is pay ' +  str(validated_data['price']) + 'rs.'
        for token in user.fcm_token:
            fb_service.sendNotification(
                message, 
                '', 
                {   
                    'notification_type': 'accountation', 
                    'last_timestamp': 'test',
                    'receiver_id' : str(user.id),
                    'sender_id' : str(validated_data['user'].id),
                    'user_name' : validated_data['user'].username,
                    'user_initial':'test',
                    'show_notification': 'true'
                },
                token
            )
        return account_management

class GetCreditDetailSerializer(BaseSerializer):
    credit = miniproject_base_serializer.SerializerMethodField()
    debit = miniproject_base_serializer.SerializerMethodField()
    # credit_date = miniproject_base_serializer.SerializerMethodField()
    # debit_date = miniproject_base_serializer.SerializerMethodField()
    created_date = miniproject_base_serializer.SerializerMethodField()
    credit_user_id = miniproject_base_serializer.SerializerMethodField()
    other_user_id =miniproject_base_serializer.SerializerMethodField()
    other_business_name=miniproject_base_serializer.SerializerMethodField()
    other_business_address=miniproject_base_serializer.SerializerMethodField()
    other_business_photo=miniproject_base_serializer.SerializerMethodField()
    other_mobile_no = miniproject_base_serializer.SerializerMethodField()
    total_balance = miniproject_base_serializer.SerializerMethodField()
    credit_user_company_name = miniproject_base_serializer.SerializerMethodField()

    class Meta:
        model = AccountManagement
        fields = ('note','credit','debit','credit_user_id','created_date','total_balance','credit_user_company_name','other_user_id','other_business_name','other_business_address','other_business_photo','other_mobile_no')

    def get_credit_user_company_name(self, accountmanagement):
        if 'user' in self.context and int(self.context['user']) == accountmanagement.credit_user.id:
            return accountmanagement.credit_user.business_name
        else:
            return accountmanagement.credit_user.business_name

    def get_credit(self, accountmanagement):
        if 'user' in self.context and int(self.context['user']) == accountmanagement.debit_user.id:
            return accountmanagement.price
        else:
            return '-'

    def get_created_date(self,accountmanagement):
        if 'user' in self.context and int(self.context['user']) == accountmanagement.credit_user.id:
            return helper.datetimeToStringDateTime(accountmanagement.created_date_time, constants.DATE_FORMAT)
        else:
            return helper.datetimeToStringDateTime(accountmanagement.created_date_time, constants.DATE_FORMAT)

    # def get_credit_date(self,accountmanagement):
    #     if 'user' in self.context and int(self.context['user']) == accountmanagement.credit_user.id:
    #         return helper.datetimeToStringDateTime(accountmanagement.created_date_time, constants.DATE_FORMAT)
    #     else:
    #         return ''

    def get_debit(self, accountmanagement):
        if 'user' in self.context and int(self.context['user']) == accountmanagement.credit_user.id:
            return accountmanagement.price
        else:
            return '-'

    def get_credit_user_id(self, accountmanagement):
        return accountmanagement.credit_user.id

    def get_other_user_id(self, accountmanagement):
        return accountmanagement.debit_user.id

    def get_other_business_name(self, accountmanagement):
        return accountmanagement.debit_user.business_name

    def get_other_business_address(self, accountmanagement):
        return accountmanagement.debit_user.address

    def get_other_business_photo(self, accountmanagement):
        return constants.NO_USER_IMAGE

    def get_other_mobile_no(self, accountmanagement):
        return accountmanagement.debit_user.phone

    # def get_debit_date(self, accountmanagement):
    #     if 'user' in self.context and int(self.context['user']) == accountmanagement.debit_user.id:
    #         return helper.datetimeToStringDateTime(accountmanagement.created_date_time, constants.DATE_FORMAT)
    #     else:
    #         return ''


    def get_total_balance(self, accountmanagement):
        total_credit_user_list = []
        account_list = AccountManagement.objects.filter(
            Q(credit_user=self.context['request_user'],debit_user__id=self.context['user']) |
            Q(debit_user=self.context['request_user'],credit_user__id=self.context['user']),
            created_date_time__lte=accountmanagement.created_date_time
        )
        # print(account_list)
        if 'user' in self.context and int(self.context['user']) == accountmanagement.debit_user.id:
            account_list = account_list.aggregate(
                total_debit_user_price = Sum(
                    Case(
                        When(debit_user=self.context['user'], then=F('price')),
                        output_field=IntegerField(),
                        default=0
                        ),
                    ),
                total_credit_user_price =  Sum(
                    Case(
                        When(credit_user=self.context['user'], then=F('price')),
                        output_field=IntegerField(),
                        default=0
                        ),
                    ), 
            )
            return account_list['total_debit_user_price']
          
            # return accountmanagement.price
        elif 'user' in self.context and int(self.context['user']) == accountmanagement.credit_user.id:
            print('in else.....')
            # account_list = account_list.filter(credit_user=self.context['user']).annotate(total_price=Coalesce(Sum('price'), 0))
            account_list = account_list.aggregate(
                total_debit_user_price = Sum(
                    Case(
                        When(debit_user=self.context['user'], then=F('price')),
                        output_field=IntegerField(),
                        default=0
                        ),
                    ),
                total_credit_user_price =  Sum(
                    Case(
                        When(credit_user=self.context['user'], then=F('price')),
                        output_field=IntegerField(),
                        default=0
                        ),
                    ), 
            )
            if account_list['total_debit_user_price'] == 0:
                return account_list['total_debit_user_price'] - account_list['total_credit_user_price']
            else:
                return account_list['total_credit_user_price'] - account_list['total_debit_user_price']

class GetDebitDetailSerializer(BaseSerializer):
    credit = miniproject_base_serializer.SerializerMethodField()
    debit = miniproject_base_serializer.SerializerMethodField()
    debit_user_id =miniproject_base_serializer.SerializerMethodField()
    credit_date = miniproject_base_serializer.SerializerMethodField()
    debit_date = miniproject_base_serializer.CharField(source='get_debit_user_date')
    credit_user_id = miniproject_base_serializer.SerializerMethodField()
    total_balance = miniproject_base_serializer.SerializerMethodField()

    class Meta:
        model = AccountManagement
        fields = ('note','debit_user_id','credit','debit','credit_date','debit_date','credit_user_id','total_balance')

    def get_credit(self, accountmanagement):
        return '-'

    def get_debit(self, accountmanagement):
        return accountmanagement.price

    def get_debit_user_id(self, accountmanagement):
        return accountmanagement.debit_user.id

    def get_credit_date(self, accountmanagement):
        return ''

    def get_credit_user_id(self, accountmanagement):
        return accountmanagement.credit_user.id

    def get_total_balance(self, accountmanagement):
        return 0

class ManageBankSerializer(BaseSerializer):
    bank_name = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Bank name is required',
        'invalid' : 'Invalid bank name',
        'blank': 'Bank name may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid bank name',
        'invalid_code' : 500
    })

    bank_account_number = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Bank account number is required',
        'invalid' : 'Invalid bank account number',
        'blank': 'Bank account number may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid bank account number',
        'invalid_code' : 500
    })

    ifac_code = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Ifac code is required',
        'invalid' : 'Invalid ifac code',
        'blank': 'Ifac code may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid ifac code',
        'invalid_code' : 500
    })

    branch_name = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Branch name is required',
        'invalid' : 'Invalid branch name',
        'blank': 'Branch name may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid branch name',
        'invalid_code' : 500
    })

    bank_location = miniproject_base_serializer.CharField(required=True, error_messages={
        'required': 'Bank location is required',
        'invalid' : 'Invalid bank location',
        'blank': 'Bank location may not be blank',
        'blank_code' : 300,
        'invalid' : 'Invalid bank location',
        'invalid_code' : 500
    })

    class Meta:
        model = BankDetails
        fields = ('bank_name','bank_account_number','ifac_code','branch_name','bank_location')

    def create(self, validated_data):
        bank_details = BankDetails(
            user = validated_data['user'],
            bank_name=validated_data['bank_name'],
            bank_account_number=validated_data['bank_account_number'],
            ifac_code=validated_data['ifac_code'],
            branch_name=validated_data['branch_name'],
            bank_location=validated_data['bank_location']
        )
        bank_details.save()
        return validated_data

class GetBankdetailSerializer(BaseSerializer):
    bank_id = miniproject_base_serializer.CharField(source='get_bank_id')
    class Meta:
        model = BankDetails
        fields = ('bank_id','bank_name','bank_account_number','ifac_code','branch_name','bank_location')