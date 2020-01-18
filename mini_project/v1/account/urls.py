from django.conf.urls import url
from v1.account import views

urlpatterns = [
   url(r'^create/', views.ManageAccount.as_view(), name='create_entry'),
]
