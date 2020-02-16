from django.conf.urls import url
from v1.account import views

urlpatterns = [
   url(r'^create/', views.ManageAccount.as_view(), name='create_entry'),
   url(r'^detail/get/', views.ManageAccount.as_view(), name='get_account_details'),
   url(r'^bank/', views.ManageBankDetails.as_view(), name='manage_bank_details'),
   
]
