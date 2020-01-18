from django.db import models
from base.models import BaseModel
from miniproject_user.models import User

class AccountManagement(BaseModel):
    class Meta:
        db_table = 'accountmanagement'

    credit_user = models.ForeignKey(User, related_name='creadit_user', on_delete=models.CASCADE)
    debit_user = models.ForeignKey(User,related_name='debit_user', on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    note = models.CharField(max_length=255,default='')
    current_time = models.DateTimeField(auto_now_add=True)
    
    