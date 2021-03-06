from django.conf.urls import url
from miniproject_user import views

urlpatterns = [
    url(r'^signup/', views.SignUp.as_view(), name='signup'),
    url(r'^signin/', views.SignIn.as_view(), name='signin'),
    url(r'^profile/update/',views.UserProfileUpdate.as_view(), name='user_profile_update'),
    url(r'^profile/get/',views.UserProfileUpdate.as_view(), name='user_profile_get') ,
    url(r'^delete',views.UserProfileUpdate.as_view(), name='user_delete'),
    url(r'^logout', views.Logout.as_view(), name='user_logout'),
    url(r'^password/update', views.ChangePassword.as_view(), name='update_password'),
    url(r'^forgot/password', views.Forgotpassword.as_view(), name='forgot_password'),
    url(r'^set/password', views.SetPassword.as_view(), name='set_password'),
    url(r'^all', views.ManageUser.as_view(), name='get_all_user'),
    url(r'^token', views.ManageUser.as_view(), name='set_token'),
    url(r'^upload/photo', views.SaveProfilePhoto.as_view(), name='user_save_photo'),
    url(r'^', views.GetAllUser.as_view(), name='get_account_all_user'),
    
]
