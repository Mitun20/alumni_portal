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
from .serializers import UserSerializer, GroupSerializer
import pandas as pd
from django.contrib.auth.models import User
from .models import *
import random
import string
from django.core.mail import send_mail
from .permissions import *



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
            
            return Response({
                'refresh': refresh_token,
                'access': access_token,
                'username': username,
                "user_id":user.id,
                'member_id':member.id if member else None
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
    permission_classes = [IsAuthenticated,IsAlumniManager]
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class Groups(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]
    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

class Assign_Group(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]
    def post(self, request):
        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            group.user_set.add(user)  # Add the user to the group
            return Response({'message': 'User added to group successfully.'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)

# Deactivate user

class DeactivateUser(APIView):
    permission_classes = [IsAuthenticated, IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumniManager]
    def post(self, request):
        salutation = Salutation(
            salutation= request.data['salutation'],
            description= request.data['description'],
        )
        salutation.save()

        return Response({"message": "Salutation created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveSalutation(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]
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
    permission_classes = [IsAuthenticated,IsAlumniManager]
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


# Create, Retrieve, and Update for Batch
class CreateBatch(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]

    def post(self, request):
        batch = Batch(
            title=request.data['title'],
            start_year=request.data['start_year'],
            end_year=request.data['end_year']
        )
        batch.save()
        return Response({"message": "Batch created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveBatch(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumniManager]

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

# Create, Retrieve, Deactivate and Update for Department
class CreateDepartment(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]

    def post(self, request):
        department = Department(
            short_name=request.data['short_name'],
            full_name=request.data['full_name'],
            is_active=request.data.get('is_active', True)
        )
        department.save()
        return Response({"message": "Department created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveDepartment(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumniManager]
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
        

# Create, Retrieve,Deactivate and Update for Course
class CreateCourse(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumniManager]
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
        
        

# register

# aluminin can register
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
                username=member.email,  # Use email as the username
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

        return Response({'message': 'Member Added successfully'}, status=status.HTTP_200_OK)


# Bulk Register by manager 
class BulkRegisterUsers(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]
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

        return Response({
            'message': message,
            'errors': errors,
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)

# Single register by manager
class SingleRegisterUser(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]
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
        course_id = request.data.get('course')
        batch_id = request.data.get('batch')
        profile_picture = request.data.get('profile_picture', None)

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

            if group_name == 'Faculty':
                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                # Create User with email as username
                try:
                    user = User.objects.create_user(
                        username=email,
                        password=password,
                        email=email,
                )
                except e:
                    return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
                

                # Add the user to the Faculty group
                faculty_group = Group.objects.get(name='Faculty')
                user.groups.add(faculty_group)

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
    permission_classes = [IsAuthenticated,IsAlumniManager]

    def post(self, request):
        skill = Skill(
            skill=request.data['skill'],
            description=request.data.get('description', '')  # Use get for optional fields
        )
        skill.save()
        return Response({"message": "Skill created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveSkill(APIView):
    permission_classes = [IsAuthenticated,IsAlumniManager]
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
    permission_classes = [IsAuthenticated,IsAlumniManager]

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
    permission_classes = [IsAuthenticated,IsAlumni]
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


# member skills
class CreateMemberSkill(APIView):
    permission_classes = [IsAuthenticated,IsAlumni]

    def post(self, request):
        try:
            member = Member.objects.get(id=request.data['member_id'])
            skill = Skill.objects.get(id=request.data['skill_id'])
            member_skill = Member_Skills(member=member, skill=skill)
            member_skill.save()
            return Response({"message": "Member skill created successfully"}, status=status.HTTP_201_CREATED)
        except (Member.DoesNotExist, Skill.DoesNotExist):
            return Response({"message": "Member or Skill not found"}, status=status.HTTP_404_NOT_FOUND)

class RetrieveMemberSkills(APIView):
    permission_classes = [IsAuthenticated,IsAlumni]
    def get(self, request,member_id):
        member_skills = Member_Skills.objects.filter(member_id=member_id)
        data = [
            {
                "skill_id": member_skill.skill.id,
            }
            for member_skill in member_skills
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateMemberSkill(APIView):
    permission_classes = [IsAuthenticated,IsAlumni]

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
    permission_classes = [IsAuthenticated,IsAlumni]

    def delete(self, request, member_skill_id):
        try:
            member_skill = Member_Skills.objects.get(id=member_skill_id)
            member_skill.delete()
            return Response({"message": "Member skill deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Member_Skills.DoesNotExist:
            return Response({"message": "Member skill not found"}, status=status.HTTP_404_NOT_FOUND)