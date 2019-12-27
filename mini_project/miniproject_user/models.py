from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from base.models import BaseModel

class UserPermission(BaseModel):
    class Meta:
        db_table = 'userpermissions'

    is_admin = models.BooleanField(default=False)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=email
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=email
        )

        user_permission = UserPermission(
            is_admin=True
        )
        user_permission.save()

        user.permissions = user_permission
        user.set_password(password)

        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,BaseModel):
    
    class Meta:
        db_table = 'users'

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, default='')
    username = models.CharField(max_length=255,default='')
    objects = UserManager()
    business_name = models.CharField(max_length=255)
    business_photo = models.CharField(max_length=255)
    photo = models.CharField(max_length=255,default='')
    about = models.TextField(default='')
    address = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=255, unique=True)
    phoneAlt = models.CharField(max_length=255,default='')
    permissions = models.ForeignKey(UserPermission, on_delete=models.CASCADE)
    USERNAME_FIELD = 'phone'
        
    def get_user_id(self):
        return self.id

    def get_phone(self):
        return self.phone
        
class BlackList(BaseModel):
    class Meta:
        db_table = 'blacklist'

    token = models.CharField('token', max_length=255,unique=True)

class UserVerification(BaseModel):
    class Meta:
        db_table = 'userverification'

    USER_VERIFICATION_TYPES = (
        ('FORGOT','forgot_password'),
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    verification_token = models.CharField(max_length=6, default="")
    verification_type = models.CharField(max_length=15, choices=USER_VERIFICATION_TYPES, default=USER_VERIFICATION_TYPES[0][0])
    verification_time = models.DateTimeField(auto_now_add=True)
