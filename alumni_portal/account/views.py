import csv
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.crypto import get_random_string
from rest_framework import status
from django.contrib.auth.models import User, Group
from .serializers import *
import pandas as pd
from django.contrib.auth.models import User
from .models import *
import random
import string
from django.core.mail import send_mail
from .permissions import *
from django.db.models import Q
from rest_framework import status


class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        member = None

        try:
            member = Member.objects.get(email=username)
        except Member.DoesNotExist:
            member = None  # Keep it None if member does not exist

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            group_names = user.groups.values_list('name', flat=True)

            # Create a dictionary with group names as keys and True as values
            group_dict = {group_name: True for group_name in group_names}

            return Response({
                'refresh': refresh_token,
                'access': access_token,
                'username': username,
                'user_id': user.id,
                'member_id': member.id if member else None,
                'groups': group_dict  # Updated to use the group dictionary
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class ForgetPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        new_password = get_random_string(length=8)
        user.set_password(new_password)
        user.save()

        send_mail(
            'Your Password has reset',
            f'Your new password is: {new_password}. Make your password with more secure',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({'message': 'Password reset token has been sent to your email'})


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('oldPassword')
        new_password = request.data.get('newPassword')

        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return Response({
            'message': 'Password has been successfully changed',
            'refresh': refresh_token,
            'access': access_token,
        })
        
# Assign Role
class Users(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
 
class Groups(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

class Assign_Group(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('id')
        group_ids = request.data.get('group_ids')  # Expecting a list of group IDs

        if not group_ids:
            return Response({'error': 'group_ids is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # If group_ids is a single value, convert it to a list
        # if isinstance(group_ids, int):
        #     group_ids = [group_ids]
        # elif not isinstance(group_ids, list):
        #     return Response({'error': 'group_ids must be a list or an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get all groups currently assigned to the user
        current_groups = set(user.groups.values_list('id', flat=True))
        new_groups = set(group_ids)

        # Determine groups to remove
        groups_to_remove = current_groups - new_groups
        # Determine groups to add
        groups_to_add = new_groups - current_groups

        # Remove user from groups no longer assigned
        for group_id in groups_to_remove:
            try:
                group = Group.objects.get(id=group_id)
                group.user_set.remove(user)
            except Group.DoesNotExist:
                continue  # If the group doesn't exist, skip

        # Add user to new groups
        for group_id in groups_to_add:
            try:
                group = Group.objects.get(id=group_id)
                group.user_set.add(user)
            except Group.DoesNotExist:
                continue  

        response_message = {
            'message': 'User groups updated successfully.',

        }

        return Response(response_message, status=status.HTTP_200_OK)
    
# Deactivate user

class DeactivateUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = request.data.get('is_active')
            user.save()
            return Response({"message": "User account deactivated successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)


# active data for dropdown
class ActiveDepartment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        departments = Department.objects.filter(is_active=True)
        data = [
            {
                "department_id": department.id,
                "short_name": department.short_name,
                "full_name": department.full_name,
                "is_active": department.is_active
            }
            for department in departments
        ]
        return Response(data, status=status.HTTP_200_OK)

class ActiveCourse(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(is_active=True)
        data = [
            {
                "course_id": course.id,
                "title": course.title,
                "graduate": course.graduate,
                "department": course.department.full_name,
                "is_active": course.is_active
            }
            for course in courses
        ]
        return Response(data, status=status.HTTP_200_OK)


# Manage Salutation
class CreateSalutation(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        salutation = Salutation(
            salutation= request.data['salutation'],
            description= request.data['description'],
        )
        salutation.save()

        return Response({"message": "Salutation created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveSalutation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        salutations = Salutation.objects.all()
        data = [
            {
                "salutation_id": salutation.id,
                "salutation_name": salutation.salutation,
                "description": salutation.description,
            }
            for salutation in salutations
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateSalutation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, salutation_id):
        try:
            salutation = Salutation.objects.get(id=salutation_id)
            data = {
                "salutation": salutation.salutation,
                "description": salutation.description,
            }
            return Response(data, status=status.HTTP_200_OK)
        except Salutation.DoesNotExist:
            return Response({"message": "Salutation not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, salutation_id):
        try:
            salutation = Salutation.objects.filter(id=salutation_id)
        except Salutation.DoesNotExist:
            return Response({"message": "Salutation not found"}, status=status.HTTP_404_NOT_FOUND)
        salutation.update(
        salutation = request.data["salutation"],
        description = request.data["description"],
        )

        return Response({"message": "Salutation updated successfully"}, status=status.HTTP_200_OK)


# manage Batch
class CreateBatch(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        batch = Batch(
            title=request.data['title'],
            start_year=request.data['start_year'],
            end_year=request.data['end_year']
        )
        batch.save()
        return Response({"message": "Batch created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveBatch(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        batches = Batch.objects.all()
        data = [
            {
                "batch_id": batch.id,
                "title": batch.title,
                "start_year": batch.start_year,
                "end_year": batch.end_year
            }
            for batch in batches
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateBatch(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        try:
            batch = Batch.objects.get(id=batch_id)
            data = {
                "title": batch.title,
                "start_year": batch.start_year,
                "end_year": batch.end_year
            }
            return Response(data, status=status.HTTP_200_OK)
        except Batch.DoesNotExist:
            return Response({"message": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, batch_id):
        try:
            batch = Batch.objects.get(id=batch_id)
        except Batch.DoesNotExist:
            return Response({"message": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)
        batch.title = request.data["title"]
        batch.start_year = request.data["start_year"]
        batch.end_year = request.data["end_year"]
        batch.save()

        return Response({"message": "Batch updated successfully"}, status=status.HTTP_200_OK)

# manage Department
class CreateDepartment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        department = Department(
            short_name=request.data['short_name'],
            full_name=request.data['full_name'],
            is_active=request.data.get('is_active', True)
        )
        department.save()
        return Response({"message": "Department created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveDepartment(APIView):
    # permission_classes = [IsAuthenticated,IsAlumniManager]

    def get(self, request):
        departments = Department.objects.all()
        data = [
            {
                "department_id": department.id,
                "short_name": department.short_name,
                "full_name": department.full_name,
                "is_active": department.is_active
            }
            for department in departments
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateDepartment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id):
        try:
            department = Department.objects.get(id=department_id)
            data = {
                "short_name": department.short_name,
                "full_name": department.full_name,
                "is_active": department.is_active
            }
            return Response(data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({"message": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, department_id):
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response({"message": "Department not found"}, status=status.HTTP_404_NOT_FOUND)
        department.short_name = request.data["short_name"]
        department.full_name = request.data["full_name"]
        department.is_active = request.data.get("is_active", department.is_active)
        department.save()

        return Response({"message": "Department updated successfully"}, status=status.HTTP_200_OK)

class InactiveDepartment(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, department_id):
        
        if department_id is None:
            return Response({"message": "Department ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            department = Department.objects.get(id=department_id)
            department.is_active = request.data.get('is_active')

            department.save()
            return Response({"message": "Department status has been updated successfully"}, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({"message": "Department not found"}, status=status.HTTP_404_NOT_FOUND)
        

# manage course
class CreateCourse(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course = Course(
            title=request.data['title'],
            graduate=request.data['graduate'],
            department_id=request.data['department_id'],  # assuming department_id is passed
            is_active=request.data.get('is_active', True)
        )
        course.save()
        return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveCourse(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.all()
        data = [
            {
                "course_id": course.id,
                "title": course.title,
                "graduate": course.graduate,
                "department": course.department.full_name,
                "department_id": course.department.id,
                "is_active": course.is_active
            }
            for course in courses
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateCourse(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request, course_id):
    #     try:
    #         course = Course.objects.get(id=course_id)
    #         data = {
    #             "title": course.title,
    #             "graduate": course.graduate,
    #             "department_id": course.department.id,
    #             "is_active": course.is_active
    #         }
    #         return Response(data, status=status.HTTP_200_OK)
    #     except Course.DoesNotExist:
    #         return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        course.title = request.data["title"]
        course.graduate = request.data["graduate"]
        course.department_id = request.data["department_id"]
        course.is_active = request.data.get("is_active", course.is_active)
        course.save()

        return Response({"message": "Course updated successfully"}, status=status.HTTP_200_OK)

class InactiveCourse(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, course_id):
        
        if course_id is None:
            return Response({"message": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course = Course.objects.get(id=course_id)
            course.is_active = request.data.get('is_active')

            course.save()
            return Response({"message": "Course status has been updated successfully"}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        

# manage Institution Views
class CreateInstitution(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        institution = Institution(
            title=request.data['title'],
            description=request.data.get('description', '')
        )
        institution.save()
        return Response({"message": "Institution created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveInstitution(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        institutions = Institution.objects.all()
        data = [{"id": inst.id, "title": inst.title, "description": inst.description} for inst in institutions]
        return Response(data, status=status.HTTP_200_OK)

class UpdateInstitution(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, institution_id):
        try:
            institution = Institution.objects.get(id=institution_id)
            data = {
                "title": institution.title,
                "description": institution.description
            }
            return Response(data, status=status.HTTP_200_OK)
        except Institution.DoesNotExist:
            return Response({"message": "Institution not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, institution_id):
        try:
            institution = Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            return Response({"message": "Institution not found"}, status=status.HTTP_404_NOT_FOUND)

        institution.title = request.data.get("title", institution.title)
        institution.description = request.data.get("description", institution.description)
        institution.save()

        return Response({"message": "Institution updated successfully"}, status=status.HTTP_200_OK)

# manage social media

class CreateSocialMedia(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        social_media = Social_Media(
            title=request.data['title'],
            icon=request.FILES['icon'],  # Assuming you're uploading a file
            url=request.data['url'],
            is_active=request.data.get('is_active', True)
        )
        social_media.save()
        return Response({"message": "Social Media entry created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveSocialMedia(APIView):
    def get(self, request):
        social_media_entries = Social_Media.objects.all()
        data = [
            {
                "id": sm.id,
                "title": sm.title,
                "icon": request.build_absolute_uri(sm.icon.url) if sm.icon else None,
                "url": sm.url,
                "is_active": sm.is_active
            }
            for sm in social_media_entries
        ]
        return Response(data, status=status.HTTP_200_OK)


class UpdateSocialMedia(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, social_media_id):
        try:
            social_media = Social_Media.objects.get(id=social_media_id)
            data = {
                "title": social_media.title,
                "icon": request.build_absolute_uri(social_media.icon.url) if social_media.icon else None,
                "url": social_media.url,
                "is_active": social_media.is_active
            }
            return Response(data, status=status.HTTP_200_OK)
        except Social_Media.DoesNotExist:
            return Response({"message": "Social Media entry not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, social_media_id):
        try:
            social_media = Social_Media.objects.get(id=social_media_id)
        except Social_Media.DoesNotExist:
            return Response({"message": "Social Media entry not found"}, status=status.HTTP_404_NOT_FOUND)

        social_media.title = request.data.get("title", social_media.title)
        if 'icon' in request.FILES:
            social_media.icon = request.FILES['icon']
        social_media.url = request.data.get("url", social_media.url)
        social_media.is_active = request.data.get("is_active", social_media.is_active)
        social_media.save()

        return Response({"message": "Social Media entry updated successfully"}, status=status.HTTP_200_OK)

class InactiveSocialMedia(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, social_media_id):
        if social_media_id is None:
            return Response({"message": "Social Media ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            social_media = Social_Media.objects.get(id=social_media_id)
            social_media.is_active = request.data.get('is_active', not social_media.is_active)
            social_media.save()
            return Response({"message": "Social Media status has been updated successfully"}, status=status.HTTP_200_OK)
        except Social_Media.DoesNotExist:
            return Response({"message": "Social Media entry not found"}, status=status.HTTP_404_NOT_FOUND)
        
# manage role
class CreateRole(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role = Role(role=request.data['role'], description=request.data.get('description', ''))
        role.save()
        return Response({"message": "Role created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveRoles(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = Role.objects.all()
        data = [{"id": role.id, "role": role.role, "description": role.description} for role in roles]
        return Response(data, status=status.HTTP_200_OK)

class UpdateRole(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, role_id):
        try:
            role = Role.objects.get(id=role_id)
            data = {
                "role": role.role,
                "description": role.description
            }
            return Response(data, status=status.HTTP_200_OK)
        except Role.DoesNotExist:
            return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, role_id):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

        role.role = request.data.get("role", role.role)
        role.description = request.data.get("description", role.description)
        role.save()

        return Response({"message": "Role updated successfully"}, status=status.HTTP_200_OK)

# manage Industry Views
class CreateIndustry(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        industry = Industry(
            title=request.data['title'],
            description=request.data['description'],
            website=request.data['website']
        )
        industry.save()
        return Response({"message": "Industry created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveIndustry(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        industries = Industry.objects.all()
        data = [{"id": ind.id, "title": ind.title, "description": ind.description, "website": ind.website} for ind in industries]
        return Response(data, status=status.HTTP_200_OK)

class UpdateIndustry(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, industry_id):
        try:
            industry = Industry.objects.get(id=industry_id)
            data = {
                "title": industry.title,
                "description": industry.description,
                "website": industry.website
            }
            return Response(data, status=status.HTTP_200_OK)
        except Industry.DoesNotExist:
            return Response({"message": "Industry not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, industry_id):
        try:
            industry = Industry.objects.get(id=industry_id)
        except Industry.DoesNotExist:
            return Response({"message": "Industry not found"}, status=status.HTTP_404_NOT_FOUND)

        industry.title = request.data.get("title", industry.title)
        industry.description = request.data.get("description", industry.description)
        industry.website = request.data.get("website", industry.website)
        industry.save()

        return Response({"message": "Industry updated successfully"}, status=status.HTTP_200_OK)

# manage Location Views
class CreateLocation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        location = Location(location=request.data['location'])
        location.save()
        return Response({"message": "Location created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveLocation(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        locations = Location.objects.all()
        data = [{"id": loc.id, "location": loc.location} for loc in locations]
        return Response(data, status=status.HTTP_200_OK)

class UpdateLocation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, location_id):
        try:
            location = Location.objects.get(id=location_id)
            data = {
                "location": location.location
            }
            return Response(data, status=status.HTTP_200_OK)
        except Location.DoesNotExist:
            return Response({"message": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, location_id):
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({"message": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

        location.location = request.data.get("location", location.location)
        location.save()

        return Response({"message": "Location updated successfully"}, status=status.HTTP_200_OK)


# manage Country 
class CreateCountry(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        country = Country(
            country_name=request.data['country_name'],
            country_code=request.data.get('country_code', '')
        )
        country.save()
        return Response({"message": "Country created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveCountry(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        countries = Country.objects.all()
        data = [{"id": country.id, "country_name": country.country_name, "country_code": country.country_code} for country in countries]
        return Response(data, status=status.HTTP_200_OK)

class UpdateCountry(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, country_id):
        try:
            country = Country.objects.get(id=country_id)
            data = {
                "country_name": country.country_name,
                "country_code": country.country_code
            }
            return Response(data, status=status.HTTP_200_OK)
        except Country.DoesNotExist:
            return Response({"message": "Country not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, country_id):
        try:
            country = Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            return Response({"message": "Country not found"}, status=status.HTTP_404_NOT_FOUND)

        country.country_name = request.data.get("country_name", country.country_name)
        country.country_code = request.data.get("country_code", country.country_code)
        country.save()

        return Response({"message": "Country updated successfully"}, status=status.HTTP_200_OK)


# register

# alumni can register
class RegisterUsers(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        # Check if email exists in Member model
        try:
            member = Member.objects.get(email=email)
        except Member.DoesNotExist:
            return Response({'error': 'Email not found in our records'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Send OTP to email
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp}',
            'noreply@yourdomain.com',
            [email],
            fail_silently=False,
        )
        
        # Store OTP in session (or any secure storage)
        # request.session['otp'] = otp
        # request.session['member_id'] = member.id

        return Response({
            'otp':otp,
            'message': 'OTP sent to email',
            'member_id': member.id
                         
            }, status=status.HTTP_200_OK)

# alumni set password
class CreatingUser(APIView):
    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        password = request.data.get('password')
        member_id = request.data.get('member_id')
        # Fetch the member object
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a user with the email as the username
        try:
            user = User.objects.create_user(
                username=member.email,
                first_name=first_name,
                last_name=last_name,
                email=member.email,
                password=password
            )
        except IntegrityError:
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        faculty_group = Group.objects.get(name='Alumni')
        user.groups.add(faculty_group)
        # Link the user to the member
        member.user = user
        member.save()

        return Response({'member_id':member.id,'message': 'User account created and linked to member successfully'}, status=status.HTTP_201_CREATED)
        
# alumni can edit member details
class ShowMemberData(APIView):
    
    def get(self, request,member_id):
        # member_id = request.data.get('member_id')
        
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        member_data = {
            'salutation': member.salutation.id,
            'gender': member.gender,
            'dob': member.dob,
            'blood_group': member.blood_group,
            'mobile_no': member.mobile_no,
            'batch': member.batch.id,
            'course': member.course.id,
            'about_me': member.about_me,
        }
        
        return Response({'member_data': member_data}, status=status.HTTP_200_OK)
    def post(self, request,member_id):
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update member fields with the new data
        member.salutation_id = request.data.get('salutation')
        member.gender = request.data.get('gender')
        member.dob = request.data.get('dob')
        member.blood_group = request.data.get('blood_group')
        member.batch_id = request.data.get('batch')
        member.course_id = request.data.get('course')
        member.about_me = request.data.get('about_me')
        member.mobile_no = request.data.get('mobile_no')

        # Save the updated member
        member.save()

        return Response({'message': 'Member Updated successfully'}, status=status.HTTP_200_OK)


# Bulk Register by manager 
class BulkRegisterUsers(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        group_name = request.data.get('group_name')
        if not group_name:
            return Response({'error': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)

        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        excel_file = request.FILES['file']
        if not (excel_file.name.endswith('.xlsx') or excel_file.name.endswith('.xls')):
            return Response({'error': 'File is not Excel type'}, status=status.HTTP_400_BAD_REQUEST)

        # Read the Excel file
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        created_users = []
        errors = []
        seen_emails = set()  # Set to track seen emails

        for index, row in df.iterrows():
            email = row['email']
            if email in seen_emails or Member.objects.filter(email=email).exists():
                errors.append({'email': email, 'error': 'Duplicate email found'})
                continue  # Skip this row if the email is a duplicate
            seen_emails.add(email)
            
            try:
                # Fetch the Salutation instance by name
                salutation = Salutation.objects.get(salutation=row['salutation'])
                
                # Fetch Batch and Course instances by their names
                batch = Batch.objects.filter(title=row['batch']).first() 
                course = Course.objects.filter(title=row['course']).first()
                
                if group_name == 'Faculty':
                    # Generate a random password
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                    # Create User with email as username
                    user = User.objects.create_user(
                        username=row['email'],
                        password=password,
                        email=row['email'],
                    )

                    # Add the user to the Faculty group
                    faculty_group = Group.objects.get(name='Faculty')
                    user.groups.add(faculty_group)

                    # Create Member
                    member = Member.objects.create(
                        user=user,
                        salutation=salutation,  # Assign the Salutation instance here
                        gender=row['gender'],
                        dob=row['dob'],
                        blood_group=row['blood_group'],
                        mobile_no=row['mobile_no'],
                        email=row['email'],
                        course=course,  # Assign the Course instance
                        batch=batch,  # Assign the Batch instance
                        profile_picture=row.get('profile_picture', None)
                    )

                    # Send email with credentials
                    send_mail(
                        subject='Your Faculty Account Details',
                        message=f'Username: {user.username}\nPassword: {password}',
                        from_email='your_email@example.com',
                        recipient_list=[user.email],
                    )

                    # created_users.append(user.username)

                else:
                    # Create Member without creating User
                    member = Member.objects.create( 
                        salutation=salutation,  # Assign the Salutation instance here
                        gender=row['gender'],
                        dob=row['dob'],
                        blood_group=row['blood_group'],
                        mobile_no=row['mobile_no'],
                        email=row['email'],
                        course=course,  # Assign the Course instance
                        batch=batch,  # Assign the Batch instance
                        profile_picture=row.get('profile_picture', None)
                    )

                    # Send email notifying them of their account
                    send_mail(
                        subject='Your Account Has Been Created',
                        message='Your member account has been created successfully.',
                        from_email='your_email@example.com',
                        recipient_list=[row['email']],
                    )

            except (Salutation.DoesNotExist, Batch.DoesNotExist, Course.DoesNotExist, Department.DoesNotExist) as e:
                errors.append({'email': row['email'], 'error': str(e)})
            except Exception as e:
                errors.append({'email': row['email'], 'error': str(e)})
        if group_name == 'Faculty':
            message = "Faculty users have been created and emails have been sent with login credentials."
        else:
            message = "Members have been created without user accounts, and notification emails have been sent."

        if errors:
             return Response({
            'errors': errors,
            }, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({
                'message': message,
                
            }, status=status.HTTP_201_CREATED)

# Single register by manager
class SingleRegisterUser(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        group_name = request.data.get('group_name')
        if not group_name:
            return Response({'error': 'Group name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract individual data from the request
        salutation_id = request.data.get('salutation_id')
        gender = request.data.get('gender')
        dob = request.data.get('dob')
        blood_group = request.data.get('blood_group')
        mobile_no = request.data.get('mobile_no')
        email = request.data.get('email')
        course_id = request.data.get('course_id')
        batch_id = request.data.get('batch_id')
        profile_picture = request.data.get('profile_picture', None)
        # print("ok 1")
        # Validate required fields
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        if Member.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Fetch the Salutation instance by ID
            salutation = Salutation.objects.get(id=salutation_id)

            # Fetch Batch, Course, Department instances by their IDs
            batch = Batch.objects.get(id=batch_id) if batch_id else None
            course = Course.objects.get(id=course_id) if course_id else None
            print("ok 2")
            if group_name == 'Faculty':
                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                # Create User with email as username
                print("ok 3")
                try:
                    user = User.objects.create_user(
                        username=email,
                        password=password,
                        email=email,
                )
                    print("ok 4")
                except e:
                    return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
                print("ok 5")

                # Add the user to the Faculty group
                faculty_group = Group.objects.get(name='Faculty')
                user.groups.add(faculty_group)
                print("ok 6")
                # Create Member
                member = Member.objects.create(
                    user=user,
                    salutation=salutation,
                    gender=gender,
                    dob=dob,
                    blood_group=blood_group,
                    mobile_no=mobile_no,
                    email=email,
                    course=course,
                    batch=batch,
                    profile_picture=profile_picture
                )

                # Send email with credentials
                send_mail(
                    subject='Your Faculty Account Details',
                    message=f'Username: {user.username}\nPassword: {password}',
                    from_email='your_email@example.com',
                    recipient_list=[user.email],
                )

                message = "Faculty user has been created and email sent with login credentials."

            else:
                # Create Member without creating User
                member = Member.objects.create(
                    salutation=salutation,
                    gender=gender,
                    dob=dob,
                    blood_group=blood_group,
                    mobile_no=mobile_no,
                    email=email,
                    course=course,
                    batch=batch,
                    profile_picture=profile_picture
                )

                # Send notification email
                send_mail(
                    subject='Your Member Account Has Been Created',
                    message='Your member account has been created successfully.',
                    from_email='your_email@example.com',
                    recipient_list=[email],
                )

                message = "Member has been created without a user account, and notification email has been sent."

            return Response({'message': message}, status=status.HTTP_201_CREATED)

        except (Salutation.DoesNotExist, Batch.DoesNotExist, Course.DoesNotExist, Department.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# manage skills

class CreateSkill(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        skill = Skill(
            skill=request.data['skill'],
            description=request.data.get('description', '')  # Use get for optional fields
        )
        skill.save()
        return Response({"message": "Skill created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveSkill(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        skills = Skill.objects.all()
        data = [
            {
                "skill_id": skill.id,
                "skill": skill.skill,
                "description": skill.description
            }
            for skill in skills
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateSkill(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, skill_id):
        try:
            skill = Skill.objects.get(id=skill_id)
            data = {
                "skill": skill.skill,
                "description": skill.description
            }
            return Response(data, status=status.HTTP_200_OK)
        except Skill.DoesNotExist:
            return Response({"message": "Skill not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, skill_id):
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return Response({"message": "Skill not found"}, status=status.HTTP_404_NOT_FOUND)

        skill.skill = request.data["skill"]
        skill.description = request.data.get("description", skill.description)  # Update if provided
        skill.save()

        return Response({"message": "Skill updated successfully"}, status=status.HTTP_200_OK)

# profile picture
class ProfilePicture(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,member_id):
        member = Member.objects.get(id=member_id)
        data = {
            "profile_picture": request.build_absolute_uri(member.profile_picture.url) if member.profile_picture else None

        }

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request,member_id):
        member = Member.objects.get(id=member_id)
        profile_picture = request.FILES.get('profile_picture')

        if not profile_picture:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the profile picture
        member.profile_picture = profile_picture
        member.save()

        return Response({'message': 'Profile picture updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request,member_id):
        member = Member.objects.get(id=member_id)

        if member.profile_picture:
            member.profile_picture.delete(save=False)  # Delete the file from storage
            member.profile_picture = None
            member.save()
            return Response({'message': 'Profile picture deleted successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No profile picture to delete'}, status=status.HTTP_404_NOT_FOUND)

# basic profile
class MemberData(APIView):
    
    def get(self, request,member_id):
        # member_id = request.data.get('member_id')
        
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        member_data = {
            'salutation': member.salutation.id,
            'first_name': member.user.first_name,
            'last_name': member.user.last_name,
            'email': member.email,
            'gender': member.gender,
            'dob': member.dob,
            'blood_group': member.blood_group,
            'mobile_no': member.mobile_no,
            'batch': member.batch.id,
            'course': member.course.id,
            'about_me': member.about_me,
        }
        
        return Response({'member_data': member_data}, status=status.HTTP_200_OK)
    def post(self, request,member_id):
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update member fields with the new data
        user= User.objects.get(email=member.email)
        
        user.first_name = request.data.get('first_name')
        user.last_name = request.data.get('last_name')
        member.salutation_id = request.data.get('salutation')
        member.email = request.data.get('email')
        user.email = member.email
        member.gender = request.data.get('gender')
        member.dob = request.data.get('dob')
        member.blood_group = request.data.get('blood_group')
        member.batch_id = request.data.get('batch')
        member.course_id = request.data.get('course')
        member.about_me = request.data.get('about_me')
        member.mobile_no = request.data.get('mobile_no')

        user.save()
        # Save the updated member
        member.save()

        return Response({'message': 'Member Updated successfully'}, status=status.HTTP_200_OK)

# ret
# manage member skills
class CreateMemberSkill(APIView):
    # permission_classes = [IsAuthenticated,IsAlumni]

    def post(self, request):
        try:
            member = Member.objects.get(id=request.data['member_id'])
            skill = Skill.objects.get(id=request.data['skill_id'])
            
            if Member_Skills.objects.filter(member=member, skill=skill).exists():
                return Response({"message": "Member already has this skill"}, status=status.HTTP_400_BAD_REQUEST)
            
            member_skill = Member_Skills(member=member, skill=skill)
            member_skill.save()
            return Response({"message": "Member skill created successfully"}, status=status.HTTP_201_CREATED)
        except (Member.DoesNotExist, Skill.DoesNotExist):
            return Response({"message": "Member or Skill not found"}, status=status.HTTP_404_NOT_FOUND)

class RetrieveMemberSkills(APIView):
    # permission_classes = [IsAuthenticated,IsAlumni]
    def get(self, request,member_id):
        member_skills = Member_Skills.objects.filter(member_id=member_id)
        data = [
            {
                "skill_id": member_skill.skill.id,
                "member_skill_id": member_skill.id,
                "skill_name":member_skill.skill.skill
            }
            for member_skill in member_skills
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateMemberSkill(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, member_skill_id):
        try:
            member_skill = Member_Skills.objects.get(id=member_skill_id)
            member = Member.objects.get(id=request.data['member_id'])
            skill = Skill.objects.get(id=request.data['skill_id'])

            member_skill.member = member
            member_skill.skill = skill
            member_skill.save()

            return Response({"message": "Member skill updated successfully"}, status=status.HTTP_200_OK)
        except Member_Skills.DoesNotExist:
            return Response({"message": "Member skill not found"}, status=status.HTTP_404_NOT_FOUND)
        except (Member.DoesNotExist, Skill.DoesNotExist):
            return Response({"message": "Member or Skill not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteMemberSkill(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, member_skill_id):
        try:
            member_skill = Member_Skills.objects.get(id=member_skill_id)
            member_skill.delete()
            return Response({"message": "Member skill deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Member_Skills.DoesNotExist:
            return Response({"message": "Member skill not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
# manage member education
class CreateMemberEducation(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MemberEducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Member education created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveMemberEducation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        education_records = Member_Education.objects.filter(member_id=member_id)
        data = []

        for record in education_records:
            data.append({
                'id': record.id,
                'institute': record.institute.title,  # Assuming institute has a 'name' field
                'degree': record.degree,
                'start_year': record.start_year,
                'end_year': record.end_year,
                'is_currently_pursuing': record.is_currently_pursuing,
                'location': record.location.location if record.location else None  # Assuming location has a 'name' field
            })

        return Response(data, status=status.HTTP_200_OK)

class UpdateMemberEducation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, education_id):
        try:
            education_record = Member_Education.objects.get(id=education_id)
            serializer = MemberEducationSerializer(education_record)  # No many=True since it's a single instance
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Member_Education.DoesNotExist:
            return Response({"message": "Member education not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, education_id):
        try:
            education = Member_Education.objects.get(id=education_id)
            serializer = MemberEducationSerializer(instance=education, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Member education updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Member_Education.DoesNotExist:
            return Response({"message": "Member education not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteMemberEducation(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, education_id):
        try:
            education = Member_Education.objects.get(id=education_id)
            education.delete()
            return Response({"message": "Member education deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Member_Education.DoesNotExist:
            return Response({"message": "Member education not found"}, status=status.HTTP_404_NOT_FOUND)

# manage member experience
class CreateMemberExperience(APIView):
    permission_classes = [IsAuthenticated]  # Uncomment if you want authentication

    def post(self, request):
        serializer = MemberExperienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Member experience created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveMemberExperience(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        experience_records = Member_Experience.objects.filter(member_id=member_id)

        # Convert the queryset to a list of dictionaries
        experience_list = [
            {
                'id': exp.id,
                'industry': exp.industry.title,  
                'role': exp.role.role if exp.role else None,  
                'start_date': exp.start_date,
                'end_date': exp.end_date,
                'is_currently_working': exp.is_currently_working,
                'location': exp.location.location  
            }
            for exp in experience_records
        ]

        return Response(experience_list, status=status.HTTP_200_OK)

class UpdateMemberExperience(APIView):
    permission_classes = [IsAuthenticated]  # Uncomment if you want authentication
    def get(self, request, experience_id):
        try:
            experience_record = Member_Experience.objects.get(id=experience_id)
            serializer = MemberExperienceSerializer(experience_record)  # Remove many=True
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Member_Experience.DoesNotExist:
            return Response({"message": "Member experience not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, experience_id):
        try:
            experience = Member_Experience.objects.get(id=experience_id)
            serializer = MemberExperienceSerializer(instance=experience, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Member experience updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Member_Experience.DoesNotExist:
            return Response({"message": "Member experience not found"}, status=status.HTTP_404_NOT_FOUND)


class DeleteMemberExperience(APIView):
    permission_classes = [IsAuthenticated]  
    def delete(self, request, experience_id):
        try:
            experience = Member_Experience.objects.get(id=experience_id)
            experience.delete()
            return Response({"message": "Member experience deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Member_Experience.DoesNotExist:
            return Response({"message": "Member experience not found"}, status=status.HTTP_404_NOT_FOUND)

# contact details for alumni
class CreateAlumni(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AlumniSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Alumni contacts created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveAlumni(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        try:
            alumni_record = Alumni.objects.get(member_id=member_id)  # Use get() here
            serializer = AlumniSerializer(alumni_record)  # No need for many=True since it's a single object
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Alumni.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except Alumni.MultipleObjectsReturned:
            return Response({"detail": "Multiple records found."}, status=status.HTTP_400_BAD_REQUEST)

class UpdateAlumni(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, member_id):
        try:
            alumni = Alumni.objects.get(member_id=member_id)
            serializer = AlumniSerializer(instance=alumni, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Alumni updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Alumni.DoesNotExist:
            return Response({"message": "Alumni record not found"}, status=status.HTTP_404_NOT_FOUND)
        

# profile status
class ProfileCompletionStatus(APIView):
    
    def get(self, request, member_id):
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Basic Profile Completion
        basic_fields = [member.salutation, member.gender, member.dob, member.email, member.mobile_no]
        basic_complete = all(basic_fields)

        # Skills Completion
        skills_complete = Member_Skills.objects.filter(member=member).exists()

        # Education Completion
        education_complete = Member_Education.objects.filter(member=member).exists()

        # Experience Completion
        experience_complete = Member_Experience.objects.filter(member=member).exists()

        # Alumni Completion (for alumni only)
        alumni_complete = True
        if Alumni.objects.filter(member=member).exists():
            alumni = Alumni.objects.get(member=member)
            alumni_complete = all([alumni.address, alumni.postal_code])

        # Calculate overall completion status
        completed_sections = sum([basic_complete, skills_complete, education_complete, experience_complete, alumni_complete])
        total_sections = 5  # Adjust based on the sections you are checking
        completion_percentage = (completed_sections / total_sections) * 100

        status = "Incomplete"
        if completion_percentage == 100:
            status = "Complete"
        elif completion_percentage >= 50:
            status = "Partially Complete"

        return Response({'completion_percentage': completion_percentage})

# list all members
class MemberListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        members = Member.objects.exclude(user__isnull=True)
        response_data = []
        for member in members:
            alumni_data = None
            if member.alumni.exists():
                alumni = member.alumni.first()
                alumni_data = {
                    'website': alumni.website,
                    'linked_in': alumni.linked_in,
                    'twitter_handle': alumni.twitter_handle,
                }
            full_name = f"{member.user.first_name} {member.user.last_name}" if member.user else None
            member_data = {
                'id': member.id,
                'name': full_name,
                'email': member.email,
                'batch': member.batch.title if member.batch else None,
                'course': member.course.title if member.course else None,
                'profile_picture': request.build_absolute_uri(member.profile_picture.url) if member.profile_picture else None,
                'alumni': alumni_data,
            }
            response_data.append(member_data)

        return Response(response_data, status=status.HTTP_200_OK)
        

# filters
class MemberFilterView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract data from the JSON body
        batch = request.data.get('batch', None)
        role = request.data.get('role', None)
        course = request.data.get('course', None)
        department = request.data.get('department', None)
        industry = request.data.get('industry', None)
        skill = request.data.get('skill', None)
        institution = request.data.get('institution', None)
        location = request.data.get('location', None)
        first_name = request.data.get('first_name', None)
        email = request.data.get('email', None)
        dob = request.data.get('dob', None)

        # Create a dictionary for the filter arguments using Q objects
        filters = Q(user__isnull=False)  # Ensure user is not null

        if batch:
            filters &= Q(batch__id=batch)
        if role:
            filters &= Q(experience__role__id=role)  # Corrected from member_experience to experience
        if course:
            filters &= Q(course__id=course)
        if department:
            filters &= Q(course__department__id=department)
        if industry:
            filters &= Q(experience__industry__id=industry)  # Corrected from member_experience to experience
        if skill:
            filters &= Q(skills__skill__id=skill)  # Corrected from member_skills to skills
        if institution:
            filters &= Q(education__institute__id=institution)  # Corrected from member_education to education
        if location:
            filters &= Q(experience__location__id=location) | Q(education__location__id=location)  # Corrected from member_experience and member_education to experience and education

        # Additional filters for personal details
        if first_name:
            filters &= Q(user__first_name__icontains=first_name)
        if email:
            filters &= Q(email__icontains=email)
        if dob:
            try:
                filters &= Q(dob=dob)  # Assuming dob is in 'YYYY-MM-DD' format
            except ValueError:
                return Response({"error": "Invalid date format for DOB. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)

        # Apply the filters to the Member queryset
        queryset = Member.objects.filter(filters).distinct()

        # Check if the queryset is empty
        if not queryset.exists():
            return Response({"message": "No matching records found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the filtered data
        response_data = []
        for member in queryset:
            alumni_data = None
            if member.alumni.exists():
                alumni = member.alumni.first()
                alumni_data = {
                    'website': alumni.website,
                    'linked_in': alumni.linked_in,
                    'twitter_handle': alumni.twitter_handle,
                }
            full_name = f"{member.user.first_name} {member.user.last_name}" if member.user else None
            member_data = {
                'id': member.id,
                'name': full_name,
                'email': member.email,
                'batch': member.batch.title if member.batch else None,
                'course': member.course.title if member.course else None,
                'profile_picture': request.build_absolute_uri(member.profile_picture.url) if member.profile_picture else None,
                'alumni': alumni_data,
            }
            response_data.append(member_data)

        return Response(response_data, status=status.HTTP_200_OK)


# detail in member
class MemberDetailView(APIView):
    def get(self, request, member_id):
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
        full_name = f"{member.user.first_name} {member.user.last_name}" if member.user else None
        # Manually construct the response data
        member_data = {
            'name': full_name,
            'email': member.email,
            'gender': member.gender,
            'dob': member.dob,
            'blood_group': member.blood_group,
            'mobile_no': member.mobile_no,
            'profile_picture': request.build_absolute_uri(member.profile_picture.url) if member.profile_picture else None,
            'about_me': member.about_me,
            'salutation': member.salutation.salutation,  # Assuming 'title' is the field in Salutation
            'batch': member.batch.title if member.batch else None,  # Adjust field as necessary
            'course': member.course.title if member.course else None,  # Adjust field as necessary
            # 'location': member.location.location if member.location else None,  # Adjust field as necessary
            'skills':[skill.skill.skill for skill in member.skills.all()],  # Adjust if related name changes
            'education': [
                {
                    'institute': edu.institute.title,  # Adjust field as necessary
                    'degree': edu.degree,
                    'start_year': edu.start_year,
                    'end_year': edu.end_year,
                    'is_currently_pursuing': edu.is_currently_pursuing,
                    'location': edu.location.location if edu.location else None  # Adjust field as necessary
                }
                for edu in member.education.all()
            ],
            'experiences': [
                {
                    'industry': exp.industry.title,  # Adjust field as necessary
                    'role': exp.role.role if exp.role else None,  # Adjust field as necessary
                    'start_date': exp.start_date,
                    'end_date': exp.end_date,
                    'is_currently_working': exp.is_currently_working,
                    'location': exp.location.location  # Adjust field as necessary
                }
                for exp in member.experience.all()
            ],
            'alumni': (
                {
                    'website': member.alumni.first().website,
                    'linked_in': member.alumni.first().linked_in,
                    'twitter_handle': member.alumni.first().twitter_handle,
                    'address': member.alumni.first().address,
                    'postal_code': member.alumni.first().postal_code,
                    'registered_on': member.alumni.first().registered_on,
                    'location':member.alumni.first().location.location
                }
                if member.alumni else None  # Check if alumni exists
            )
        }

        return Response(member_data, status=status.HTTP_200_OK)