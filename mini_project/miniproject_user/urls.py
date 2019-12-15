from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^signup/', views.SignUp.as_view(), name='signup'),
    url(r'^signin/', views.SignIn.as_view(), name='signin'),
    url(r'^profile/update/',views.UserProfileUpdate.as_view(), name='user_profile_update'),
    url(r'^profile/get',views.UserProfileUpdate.as_view(), name='user_profile_get') ,
    url(r'^delete',views.UserProfileUpdate.as_view(), name='user_delete'),
    url(r'^logout', views.Logout.as_view(), name='user_logout'),
    url(r'^password/update', views.ChangePassword.as_view(), name='password')
]
