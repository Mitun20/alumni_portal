# views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import *
from account.models import *
from .serializers import *
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from account.permissions import *

class CreateJobPost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        industry = Industry.objects.get(id=request.data.get('industry'))
        role = Role.objects.get(id=request.data.get('role'))
        job_post = JobPost(
            posted_by=request.user,
            job_title=request.data.get('job_title'),
            industry=industry,
            experience_level_from=request.data.get('experience_level_from'),
            experience_level_to=request.data.get('experience_level_to'),
            location=request.data.get('location'),
            contact_email=request.data.get('contact_email'),
            contact_link=request.data.get('contact_link'),
            role=role,
            salary_package=request.data.get('salary_package'),
            dead_line=request.data.get('dead_line'),
            job_description=request.data.get('job_description'),
            file=request.FILES.get('file'),
            post_type=request.data.get('post_type')
        )
        
        job_post.save()
        job_post.skills.set(request.data.getlist('skills'))  # Assuming skills is a list of IDs
        return Response({"message": "Job post created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveJobPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        job_posts = JobPost.objects.all()
        
        # Manually create a list of job post data
        job_posts_data = []
        for job in job_posts:
            job_posts_data.append({
                'id': job.id,
                # 'posted_by': job.posted_by.username,  # Assuming User has a username field
                'job_title': job.job_title,
                'industry': job.industry.title,  # Adjust based on your Industry model
                # 'experience_level_from': job.experience_level_from,
                # 'experience_level_to': job.experience_level_to,
                'location': job.location,
                # 'contact_email': job.contact_email,
                # 'contact_link': job.contact_link,
                'role': job.role.role,  # Adjust based on your Role model
                # 'skills': [skill.skill for skill in job.skills.all()],  # List of skill names
                'salary_package': job.salary_package,
                'dead_line': job.dead_line,
                # 'job_description': job.job_description,
                'file': request.build_absolute_uri(job.file.url) if job.file else None,
                # 'post_type': job.post_type,
                'posted_on': job.posted_on,
                # 'is_active': job.is_active,
            })

        return Response(job_posts_data, status=status.HTTP_200_OK)

class MainRetrieveJobPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        job_posts = JobPost.objects.annotate(application_count=Count('application'))
        
        # Manually create a list of job post data
        job_posts_data = []
        for job in job_posts:
            job_posts_data.append({
                'id': job.id,
                # 'posted_by': job.posted_by.username,  # Assuming User has a username field
                'job_title': job.job_title,
                'industry': job.industry.title,  # Adjust based on your Industry model
                # 'experience_level_from': job.experience_level_from,
                # 'experience_level_to': job.experience_level_to,
                'location': job.location,
                # 'contact_email': job.contact_email,
                # 'contact_link': job.contact_link,
                'role': job.role.role,  # Adjust based on your Role model
                # 'skills': [skill.skill for skill in job.skills.all()],  # List of skill names
                'salary_package': job.salary_package,
                # 'dead_line': job.dead_line,
                # 'job_description': job.job_description,
                'file': request.build_absolute_uri(job.file.url) if job.file else None,
                # 'post_type': job.post_type,
                'posted_on': job.posted_on,
                'is_active': job.is_active,
                'application_count': job.application_count,
            })

        return Response(job_posts_data, status=status.HTTP_200_OK)
    
class MyJobPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            job_posts = JobPost.objects.filter(posted_by=request.user).annotate(application_count=Count('application'))

            job_posts_data = []
            for job in job_posts:
                job_posts_data.append({
                    'id': job.id,
                    'job_title': job.job_title,
                    'industry': job.industry.title,  # Adjust based on your Industry model
                    'location': job.location,
                    'role': job.role.role,  # Adjust based on your Role model
                    'salary_package': job.salary_package,
                    'file': request.build_absolute_uri(job.file.url) if job.file else None,
                    'posted_on': job.posted_on,
                    'application_count': job.application_count,  # Number of applications for this job post
                    'is_active': job.is_active,
                })

            return Response(job_posts_data, status=status.HTTP_200_OK)
        except JobPost.DoesNotExist:
            return Response({"message": "Job post not found"}, status=status.HTTP_404_NOT_FOUND)
                        
class UpdateJobPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            job_post = JobPost.objects.get(id=post_id)
            serializer = JobPostSerializer(job_post, context={'request': request})  # Pass the request context
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobPost.DoesNotExist:
            return Response({"message": "Job post not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, post_id):
        try:
            job_post = JobPost.objects.get(id=post_id)
        except JobPost.DoesNotExist:
            return Response({"message": "Job post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Assuming you want to check for permissions
        # if job_post.posted_by != request.user:
        #     return Response({"message": "You do not have permission to Edit this comment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobPostUpdateSerializer(job_post, data=request.data)
        
        if serializer.is_valid():
            # Handle file upload if it exists
            if 'file' in request.FILES:
                job_post.file = request.FILES['file']
                
            serializer.save()  # This will call the update method in the serializer
            return Response({"message": "Job post updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InactivateJobPost(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, post_id):
        if post_id is None:
            return Response({"message": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job_post = JobPost.objects.get(id=post_id)
            job_post.is_active = request.data.get('is_active', False)
            job_post.save()
            return Response({"message": "Job post status updated successfully"}, status=status.HTTP_200_OK)
        except JobPost.DoesNotExist:
            return Response({"message": "Job post not found"}, status=status.HTTP_404_NOT_FOUND)
        
class DetailJobPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            job = JobPost.objects.get(id=post_id)
        
        # Manually create a list of job post data
           
            job_posts_data={
                    
                    'posted_by': job.posted_by.username,  # Assuming User has a username field
                    'job_title': job.job_title,
                    'industry': job.industry.title,  # Adjust based on your Industry model
                    'experience_level_from': job.experience_level_from,
                    'experience_level_to': job.experience_level_to,
                    'location': job.location,
                    'contact_email': job.contact_email,
                    'contact_link': job.contact_link,
                    'role': job.role.role,  # Adjust based on your Role model
                    'skills': [skill.skill for skill in job.skills.all()],  # List of skill names
                    'salary_package': job.salary_package,
                    'dead_line': job.dead_line,
                    'job_description': job.job_description,
                    'file': request.build_absolute_uri(job.file.url) if job.file else None,
                    'posted_on': job.posted_on,
                }

            return Response(job_posts_data, status=status.HTTP_200_OK)
        except JobPost.DoesNotExist:
            return Response({"message": "Job post not found"}, status=status.HTTP_404_NOT_FOUND)


# manage Business Directory
class CreateBusinessDirectory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        business_directory = BusinessDirectory(
            business_name=request.data.get('business_name'),
            description=request.data.get('description'),
            website=request.data.get('website'),
            industry_type_id=request.data.get('industry_type'),
            location=request.data.get('location'),
            contact_email=request.data.get('contact_email'),
            contact_number=request.data.get('contact_number'),
            country_code_id=request.data.get('country_code'),
            are_you_part_of_management=request.data.get('are_you_part_of_management', True),
            logo=request.FILES.get('logo'),
            listed_by=request.user
        )
        
        business_directory.save()
        return Response({"message": "Business directory entry created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveBusinessDirectory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            business_directories = BusinessDirectory.objects.all()
            data = []
            for business in business_directories:
                data.append({
                    "id": business.id,
                    "business_name": business.business_name,
                    # "description": business.description,
                    "website": business.website,
                    "industry_type": business.industry_type.id,  # or business.industry_type.name if you want the name
                    "location": business.location,
                    # "contact_email": business.contact_email,
                    # "contact_number": business.contact_number,
                    # "country_code": business.country_code.id,  # or business.country_code.name if you want the name
                    # "are_you_part_of_management": business.are_you_part_of_management,
                     "logo": request.build_absolute_uri(business.logo.url) if business.logo else None,
                    "listed_on": business.listed_on,
                    # "listed_by": business.listed_by.id,  # or business.listed_by.username if you want the username
                })
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MyBusinessDirectory(APIView):
    def get(self, request):
        try:
            business_directories = BusinessDirectory.objects.filter(listed_by=request.user)
            data = []
            for business in business_directories:
                data.append({
                    "id": business.id,
                    "business_name": business.business_name,
                    # "description": business.description,
                    "website": business.website,
                    "industry_type": business.industry_type.type_name, 
                    "location": business.location,
                    # "contact_email": business.contact_email,
                    # "contact_number": business.contact_number,
                    # "country_code": business.country_code.country_code,  
                    # "are_you_part_of_management": business.are_you_part_of_management,
                     "logo": request.build_absolute_uri(business.logo.url) if business.logo else None,
                    "listed_on": business.listed_on,
                    # "listed_by": business.listed_by.id,  # or business.listed_by.username if you want the username
                })
            return Response(data, status=status.HTTP_200_OK)
        
        except BusinessDirectory.DoesNotExist:
            return Response({"message": "Business directory not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateBusinessDirectory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, directory_id):
        try:
            business_directories = BusinessDirectory.objects.filter(id=directory_id)
            data = []
            for business in business_directories:
                data.append({
                    "id": business.id,
                    "business_name": business.business_name,
                    "description": business.description,
                    "website": business.website,
                    "industry_type": business.industry_type.type_name, 
                    "location": business.location,
                    "contact_email": business.contact_email,
                    "contact_number": business.contact_number,
                    "country_code": business.country_code.country_code,  
                    "are_you_part_of_management": business.are_you_part_of_management,
                     "logo": request.build_absolute_uri(business.logo.url) if business.logo else None,
                    "listed_on": business.listed_on,
                    "listed_by": business.listed_by.id,  # or business.listed_by.username if you want the username
                })
            return Response(data, status=status.HTTP_200_OK)
        
        except BusinessDirectory.DoesNotExist:
            return Response({"message": "Business directory not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, directory_id):
        try:
            business_directory = BusinessDirectory.objects.get(id=directory_id)
        except BusinessDirectory.DoesNotExist:
            return Response({"message": "Business directory not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update fields
        business_directory.business_name = request.data.get('business_name', business_directory.business_name)
        business_directory.description = request.data.get('description', business_directory.description)
        business_directory.website = request.data.get('website', business_directory.website)
        business_directory.industry_type_id = request.data.get('industry_type', business_directory.industry_type_id)
        business_directory.location = request.data.get('location', business_directory.location)
        business_directory.contact_email = request.data.get('contact_email', business_directory.contact_email)
        business_directory.contact_number = request.data.get('contact_number', business_directory.contact_number)
        business_directory.country_code_id = request.data.get('country_code', business_directory.country_code_id)
        business_directory.are_you_part_of_management = request.data.get('are_you_part_of_management', business_directory.are_you_part_of_management)

        # Handle logo upload
        if request.FILES.get('logo'):
            business_directory.logo = request.FILES.get('logo')

        business_directory.save()
        return Response({"message": "Business directory entry updated successfully"}, status=status.HTTP_200_OK)

class DetailBusinessDirectory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, directory_id):
        try:
            business_directory = BusinessDirectory.objects.get(id=directory_id)
            data = {
                "business_name": business_directory.business_name,
                "description": business_directory.description,
                "website": business_directory.website,
                "industry_type": business_directory.industry_type.type_name,  # or business_directory.industry_type.name
                "location": business_directory.location,
                "contact_email": business_directory.contact_email,
                "contact_number": business_directory.contact_number,
                "country_code": business_directory.country_code.country_code,  # or business_directory.country_code.name
                "logo": business_directory.logo.url if business_directory.logo else None,
                "listed_on": business_directory.listed_on,
                "listed_by": business_directory.listed_by.username,  # or business_directory.listed_by.username
            }
            return Response(data, status=status.HTTP_200_OK)
        except BusinessDirectory.DoesNotExist:
            return Response({"message": "Business directory not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# filter job post

class JobPostFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract data from the JSON body
        job_title = request.data.get('job_title', None)
        industry_id = request.data.get('industry', None)  # Assuming you're passing the industry ID
        location = request.data.get('location', None)
        role_id = request.data.get('role', None)  # Assuming you're passing the role ID
        post_type = request.data.get('post_type', None)

        # Create a dictionary for the filter arguments
        filters = Q()
        if job_title:
            filters &= Q(job_title__icontains=job_title)
        if industry_id:
            filters &= Q(industry_id=industry_id)
        if location:
            filters &= Q(location__icontains=location)
        if role_id:
            filters &= Q(role_id=role_id)
        if post_type:
            filters &= Q(post_type__icontains=post_type)

        # Apply the filters in a single query
        queryset = JobPost.objects.filter(filters).annotate(application_count=Count('application'))

        # Prepare the response data without serializers
        data = []
        for job in queryset:
            data.append({
                "id": job.id,
                "job_title": job.job_title,
                "industry": job.industry.title,  
                "location": job.location,
                "role": job.role.role,
                "posted_on": job.posted_on,
                "is_active": job.is_active,
                'application_count': job.application_count,
            })

        return Response(data, status=status.HTTP_200_OK)

# filter Business directory

class BusinessDirectoryFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract data from the JSON body
        business_name = request.data.get('business_name', None)
        industry_id = request.data.get('industry', None)  # Assuming you're passing the industry ID
        location = request.data.get('location', None)

        # Create a dictionary for the filter arguments
        filters = Q()
        if business_name:
            filters &= Q(business_name__icontains=business_name)
        if industry_id:
            filters &= Q(industry_type_id=industry_id)
        if location:
            filters &= Q(location__icontains=location)


        # Apply the filters in a single query
        queryset = BusinessDirectory.objects.filter(filters)

        # Prepare the response data
        data = []
        for business in queryset:
            data.append({
                "id": business.id,
                "business_name": business.business_name,
                "website": business.website,
                "industry": business.industry_type.type_name,  # Assuming you want the industry name
                "location": business.location,
                "contact_email": business.contact_email,
                "listed_on": business.listed_on,
                "logo": request.build_absolute_uri(business.logo.url) if business.logo else None,
            })

        return Response(data, status=status.HTTP_200_OK)

# manage comments
class CreateJobComment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(JobPost, id=job_id)
        comment_text = request.data.get('comment')
        
        if not comment_text:
            return Response({"error": "Comment text is required."}, status=status.HTTP_400_BAD_REQUEST)

        comment = JobComment(
            job=job,
            comment_by=request.user,
            comment=comment_text
        )
        comment.save()
        return Response({"message": "Comment created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveJobComments(APIView):
    def get(self, request, job_id):
        comments = JobComment.objects.filter(job_id=job_id)
        data = [
            {
                "comment_id": comment.id,
                "comment_by": comment.comment_by.username,
                "comment": comment.comment,
            }
            for comment in comments
        ]
        return Response(data, status=status.HTTP_200_OK)

class DeleteJobComment(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(JobComment, id=comment_id)

        # Check if the comment was made by the requesting user
        if comment.comment_by != request.user:
            return Response({"message": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Applications

class CreateApplication(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,job_post_id):
        job_post = JobPost.objects.get(id=job_post_id)
        
        application = Application(
            job_post=job_post,
            full_name=request.data.get('full_name'),
            email=request.data.get('email'),
            mobile_number=request.data.get('mobile_number'),
            current_industry_id=request.data.get('current_industry'),
            current_role_id=request.data.get('current_role'),
            total_years_of_experience=request.data.get('total_years_of_experience'),
            notes_to_recruiter=request.data.get('notes_to_recruiter'),
            resume=request.FILES.get('resume')
        )
        
        application.save()
        application.skills.set(request.data.getlist('skills'))  # Assuming skills is a list of IDs

        # Send email to the job post's posted user
        self.send_email_notification(job_post.posted_by.email, application)

        return Response({"message": "Application submitted successfully"}, status=status.HTTP_201_CREATED)

    def send_email_notification(self, recipient_email, application):
        subject = f"New Application for {application.job_post.job_title}"
        message = f"""
        Hello,

        You have received a new application for the job '{application.job_post.job_title}'.

        Applicant Name: {application.full_name}
        Email: {application.email}
        Mobile Number: {application.mobile_number}
        Current Role: {application.current_role.role}
        Total Years of Experience: {application.total_years_of_experience}
        Notes to Recruiter: {application.notes_to_recruiter}

        Best regards,
        Your Job Portal
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Ensure you have DEFAULT_FROM_EMAIL set in your settings
            [recipient_email],
            fail_silently=False,
        )

# class RetrieveApplication(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
        
#         applications = Application.objects.all()
        
#         applications_data = []
#         for application in applications:
#             applications_data.append({
#                 'id': application.id,
#                 'full_name': application.full_name,
#                 'email': application.email,
#                 # 'mobile_number': application.mobile_number,
#                 # 'current_industry': application.current_industry.title,  # Adjust based on your Industry model
#                 'current_role': application.current_role.title,  # Adjust based on your Role model
#                 'total_years_of_experience': application.total_years_of_experience,
#                 # 'skills': [skill.skill for skill in application.skills.all()],  # List of skill names
#                 # 'applied_on': application.applied_on,
#                 'resume': request.build_absolute_uri(application.resume.url) if application.resume else None,
#                 # 'notes_to_recruiter': application.notes_to_recruiter,
#             })

#         return Response(applications_data, status=status.HTTP_200_OK)

class MyJobApplication(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request,job_post_id):
        # Get the job posts created by the authenticated user
        job_post = JobPost.objects.get(id=job_post_id)

        # Get applications for those job posts
        applications = Application.objects.filter(job_post=job_post)

        applications_data = []
        for application in applications:
            applications_data.append({
                'id': application.id,
                'full_name': application.full_name,
                'email': application.email,
                'current_role': application.current_role.role,  # Adjust based on your Role model
                'total_years_of_experience': application.total_years_of_experience,
                'resume': request.build_absolute_uri(application.resume.url) if application.resume else None,
            })

        return Response(applications_data, status=status.HTTP_200_OK)

class DetailViewApplication(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,application_id):
        
        application = Application.objects.get(id=application_id)

        
        applications_data={
                'id': application.id,
                'job_name': application.job_post.job_title,
                'full_name': application.full_name,
                'email': application.email,
                'mobile_number': application.mobile_number,
                'current_industry': application.current_industry.title,  # Adjust based on your Industry model
                'current_role': application.current_role.role,  # Adjust based on your Role model
                'total_years_of_experience': application.total_years_of_experience,
                'skills': [skill.skill for skill in application.skills.all()],  # List of skill names
                'applied_on': application.applied_on,
                'resume': request.build_absolute_uri(application.resume.url) if application.resume else None,
                'notes_to_recruiter': application.notes_to_recruiter,
        }

        return Response(applications_data, status=status.HTTP_200_OK)