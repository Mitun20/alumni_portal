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
    path('deactivate_user/<int:user_id>/', DeactivateUser.as_view(), name='deactivate_user'),

    # alumni registration process
    path('register_user/', RegisterUsers.as_view(), name='register_user'),
    path('creating_user/',CreatingUser.as_view(),name='creating_user'),
    path('member_data/<int:member_id>/',ShowMemberData.as_view(),name='member_data'),

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
    path('decativate_department/<int:department_id>/', InactiveDepartment.as_view(), name='decativate_department'),

    # Course
    path('create_course/', CreateCourse.as_view(), name='create_course'),
    path('retrieve_course/', RetrieveCourse.as_view(), name='retrieve_course'),
    path('update_course/<int:course_id>/', UpdateCourse.as_view(), name='update_course'),
    path('decativate_course/<int:course_id>/', InactiveCourse.as_view(), name='decativate_course'),

    # Active department and course
    path('active_department/', ActiveDepartment.as_view(), name='active_department'),
    path('active_course/', ActiveCourse.as_view(), name='active_course'),

    # Skills
    path('create_skill/', CreateSkill.as_view(), name='create_skill'),  
    path('retrieve_skills/', RetrieveSkill.as_view(), name='retrieve_skills'),  
    path('update_skill/<int:skill_id>/', UpdateSkill.as_view(), name='update_skill'),
    
    # edit Profile
    path('profile_picture/<int:member_id>/', ProfilePicture.as_view(), name='profile_picture'),
    path('update_member/<int:member_id>/', MemberData.as_view(), name='update_member'),

    # member skills
    path('create_member_skill/', CreateMemberSkill.as_view(), name='create_member_skill'), 
    path('retrieve_member_skills/<int:member_id>/', RetrieveMemberSkills.as_view(), name='retrieve_member_skills'),  
    path('update_member_skill/<int:member_skill_id>/', UpdateMemberSkill.as_view(), name='update_member_skill'),  
    path('delete_member_skill/<int:member_skill_id>/', DeleteMemberSkill.as_view(), name='delete_member_skill'),

    # member education
    path('create_member_education/', CreateMemberEducation.as_view(), name='create_member_education'), 
    path('retrieve_member_education/<int:member_id>/', RetrieveMemberEducation.as_view(), name='retrieve_member_education'), 
    path('update_member_education/<int:education_id>/', UpdateMemberEducation.as_view(), name='update_member_education'),  
    path('delete_member_education/<int:education_id>/', DeleteMemberEducation.as_view(), name='delete_member_education'),

    # member experience
    path('create_member_experience/', CreateMemberExperience.as_view(), name='create_member_experience'),
    path('retrieve_member_experience/<int:member_id>/', RetrieveMemberExperience.as_view(), name='retrieve_member_experience'),
    path('update_member_experience/<int:experience_id>/', UpdateMemberExperience.as_view(), name='update_member_experience'),
    path('delete_member_experience/<int:experience_id>/', DeleteMemberExperience.as_view(), name='delete_member_experience'),

    # Institution 
    path('create_institution/', CreateInstitution.as_view(), name='create_institution'),
    path('retrieve_institutions/', RetrieveInstitution.as_view(), name='retrieve_institution'),
    path('update_institution/<int:institution_id>/', UpdateInstitution.as_view(), name='update_institution'),

    # Role
    path('create_role/', CreateRole.as_view(), name='create_role'),
    path('retrieve_role/', RetrieveRoles.as_view(), name='retrieve_role'),
    path('update_role/<int:role_id>/', UpdateRole.as_view(), name='update_role'),

    # Industry 
    path('create_industry/', CreateIndustry.as_view(), name='create_industry'),
    path('retrieve_industries/', RetrieveIndustry.as_view(), name='retrieve_industries'),
    path('update_industry/<int:industry_id>/', UpdateIndustry.as_view(), name='update_industry'),

    # Location 
    path('create_location/', CreateLocation.as_view(), name='create_location'),
    path('retrieve_locations/', RetrieveLocation.as_view(), name='retrieve_locations'),
    path('update_location/<int:location_id>/', UpdateLocation.as_view(), name='update_location'),

    # Country 
    path('create_country/', CreateCountry.as_view(), name='create_country'),
    path('retrieve_countries/', RetrieveCountry.as_view(), name='retrieve_countries'),
    path('update_country/<int:country_id>/', UpdateCountry.as_view(), name='update_country'),

    # Alumni contacts
    path('create_alumni/', CreateAlumni.as_view(), name='create_alumni'),
    path('retrieve_alumni/<int:member_id>/', RetrieveAlumni.as_view(), name='retrieve_alumni'),
    path('update_alumni/<int:member_id>/', UpdateAlumni.as_view(), name='update_alumni'),

    # filters 
    path('filter_by/', MemberFilterView.as_view(), name='filter_by'),
    path('detail_view/<int:member_id>/', MemberDetailView.as_view(), name='detail_view'),

    #Social media
    path('create_social_media/', CreateSocialMedia.as_view(), name='create_social_media'),
    path('retrieve_social_media/', RetrieveSocialMedia.as_view(), name='retrieve_social_media'),
    path('update_social_media/<int:social_media_id>/', UpdateSocialMedia.as_view(), name='update_social_media'),
    path('deactivate_social_media/<int:social_media_id>/', InactiveSocialMedia.as_view(), name='deactivate_social_media'),
    
]
