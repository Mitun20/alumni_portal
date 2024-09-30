from django.urls import path
from .views import *



urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('forget_password/', ForgetPassword.as_view(), name='forget_password'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('users/', Users.as_view(), name='user_list'),
    path('groups/', Groups.as_view(), name='group_list'),
    path('assign_group/', Assign_Group.as_view(), name='assign_group'),
    path('register_user/', RegisterUsers.as_view(), name='register_user'),
    path('bulk_import_users/', BulkRegisterUsers.as_view(), name='bulk_import_users'),
    path('creating_user/',CreatingUser.as_view(),name='creating_user'),
    path('member_data/',ShowMemberData.as_view(),name='member_data'),
    path('single_import_users/', SingleRegisterUser.as_view(), name='single_import_users'),
    path('salutation_data/',RetrieveSalutation.as_view(),name='salutation_data'),
    path('_data/',ShowMemberData.as_view(),name='member_data'),
    path('_data/',ShowMemberData.as_view(),name='member_data'),
    path('_data/',ShowMemberData.as_view(),name='member_data'),
]