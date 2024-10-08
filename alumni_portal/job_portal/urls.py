from django.urls import path
from .views import *

urlpatterns = [
    # Job Post 
    path('create_job_post/', CreateJobPost.as_view(), name='create_job_post'),
    path('retrieve_job_post/', RetrieveJobPost.as_view(), name='retrieve_job_post'),
    path('my_job_post/', MyJobPost.as_view(), name='my_job_post'),  
    path('update_job_post/<int:post_id>/', UpdateJobPost.as_view(), name='update_job_post'),
    path('deactivate_job_post/<int:post_id>/', InactivateJobPost.as_view(), name='deactivate_job_post'),
    path('detail_job_post/<int:post_id>/', DetailJobPost.as_view(), name='detail_job_post'),

    # Business
    path('create_business_directory/', CreateBusinessDirectory.as_view(), name='create_business_directory'),
    path('retrieve_business_directory/', RetrieveBusinessDirectory.as_view(), name='retrieve_business_directory'),
    path('my_business_directory/', MyBusinessDirectory.as_view(), name='my_business_directory'),
    path('update_business_directory/<int:directory_id>/', UpdateBusinessDirectory.as_view(), name='update_business_directory'),
    path('deactivate_business_directory/<int:directory_id>/', InactivateBusinessDirectory.as_view(), name='deactivate_business_directory'),
    path('detail_business_directory/<int:directory_id>/', DetailBusinessDirectory.as_view(), name='detail_business_directory'),
]
