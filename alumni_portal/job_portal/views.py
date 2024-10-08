# views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import *
from account.models import *
from .serializers import *

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
                # 'dead_line': job.dead_line,
                # 'job_description': job.job_description,
                'file': request.build_absolute_uri(job.file.url) if job.file else None,
                # 'post_type': job.post_type,
                'posted_on': job.posted_on,
                # 'is_active': job.is_active,
            })

        return Response(job_posts_data, status=status.HTTP_200_OK)
    
class MyJobPost(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            job_posts = JobPost.objects.filter(posted_by=request.user)
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
                    # 'is_active': job.is_active,
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
        
        industry = Industry.objects.get(id=request.data.get('industry'))
        role = Role.objects.get(id=request.data.get('role'))
        # Update fields
        job_post.job_title = request.data.get('job_title', job_post.job_title)
        job_post.industry = industry
        job_post.experience_level_from = request.data.get('experience_level_from', job_post.experience_level_from)
        job_post.experience_level_to = request.data.get('experience_level_to', job_post.experience_level_to)
        job_post.location = request.data.get('location', job_post.location)
        job_post.contact_email = request.data.get('contact_email', job_post.contact_email)
        job_post.contact_link = request.data.get('contact_link', job_post.contact_link)
        job_post.role = role
        job_post.salary_package = request.data.get('salary_package', job_post.salary_package)
        job_post.dead_line = request.data.get('dead_line', job_post.dead_line)
        job_post.job_description = request.data.get('job_description', job_post.job_description)

        # Handle file upload
        if request.FILES.get('file'):
            job_post.file = request.FILES.get('file')

        job_post.save()
        job_post.skills.set(request.data.getlist('skills', []))  # Update skills
        return Response({"message": "Job post updated successfully"}, status=status.HTTP_200_OK)


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
            job_posts = JobPost.objects.get(id=post_id)
        
        # Manually create a list of job post data
            job_posts_data = []
            for job in job_posts:
                job_posts_data.append({
                    
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
                })

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

class InactivateBusinessDirectory(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, directory_id):
        if directory_id is None:
            return Response({"message": "Directory ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            business_directory = BusinessDirectory.objects.get(id=directory_id)
            # Assuming you have an `is_active` field
            business_directory.is_active = request.data.get('is_active', False)
            business_directory.save()
            return Response({"message": "Business directory status updated successfully"}, status=status.HTTP_200_OK)
        except BusinessDirectory.DoesNotExist:
            return Response({"message": "Business directory not found"}, status=status.HTTP_404_NOT_FOUND)

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
