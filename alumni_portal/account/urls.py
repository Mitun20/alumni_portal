from django.urls import path
from .views import *



urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('forget_password/', ForgetPassword.as_view(), name='forget_password'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    
    # get users, groups and assign 
    path('users/', Users.as_view(), name='user_list'),
    path('groups/', Groups.as_view(), name='group_list'),
    path('assign_group/', Assign_Group.as_view(), name='assign_group'),
    
    # alumni registration process
    path('register_user/', RegisterUsers.as_view(), name='register_user'),
    path('creating_user/',CreatingUser.as_view(),name='creating_user'),
    path('member_data/',ShowMemberData.as_view(),name='member_data'),
    
    # single or multiple created by manager
    path('single_import_users/', SingleRegisterUser.as_view(), name='single_import_users'),
    path('bulk_import_users/', BulkRegisterUsers.as_view(), name='bulk_import_users'),
    
    # Salutation
    path('create_salutation/',CreateSalutation.as_view(),name='create_salutation'),
    path('retrieve_salutation/',RetrieveSalutation.as_view(),name='retrieve_salutation'),
    path('update_salutation/<int:salutation_id>/',UpdateSalutation.as_view(),name='update_salutation'),
    
    # Batch
    path('create_batch/', CreateBatch.as_view(), name='create_batch'),
    path('retrieve_batch/', RetrieveBatch.as_view(), name='retrieve_batch'),
    path('update_batch/<int:batch_id>/', UpdateBatch.as_view(), name='update_batch'),

    # Department
    path('create_department/', CreateDepartment.as_view(), name='create_department'),
    path('retrieve_department/', RetrieveDepartment.as_view(), name='retrieve_department'),
    path('update_department/<int:department_id>/', UpdateDepartment.as_view(), name='update_department'),

    # Course
    path('retrieve_course/', CreateCourse.as_view(), name='retrieve_course'),
    path('retrieve_course/', RetrieveCourse.as_view(), name='retrieve_course'),
    path('update_course/<int:course_id>/', UpdateCourse.as_view(), name='update_course'),
]