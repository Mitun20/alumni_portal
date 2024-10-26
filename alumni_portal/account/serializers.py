from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import *

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username','is_active','groups']  # Add any other fields you need

    def get_groups(self, obj):
        return [{"id": group.id, "name": group.name} for group in obj.groups.all()]

         
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class MemberEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member_Education
        fields = ['id', 'member', 'institute', 'degree', 'start_year', 'end_year', 'is_currently_pursuing', 'location']

class MemberExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member_Experience
        fields = ['id', 'member', 'industry', 'role', 'start_date', 'end_date', 'is_currently_working', 'location']
        
# class BatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Batch
#         fields = ['name']  # Adjust this to match your model fields

# class CourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = ['name']  # Adjust this to match your model fields

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name']  # Adjust this to match your model fields

# class SalutationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Salutation
#         fields = ['title']  # Adjust this to match your model fields

# class AlumniSerializer(serializers.ModelSerializer):
#     location = LocationSerializer()
#     class Meta:
#         model = Alumni
#         fields = '__all__'  # Adjust fields as needed


class AlumniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumni
        fields = ['id', 'member', 'website', 'linked_in', 'twitter_handle', 'address', 'location', 'postal_code', 'registered_on']


# class SkillSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Member_Skills
#         fields = ['skill']

# class EducationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Member_Education
#         fields = ['institute', 'degree', 'start_year', 'end_year', 'is_currently_pursuing', 'location']

# class ExperienceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Member_Experience
#         fields = ['industry', 'role', 'start_date', 'end_date', 'is_currently_working', 'location']
    
    
# class MemberDetailSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source='user.first_name')
#     last_name = serializers.CharField(source='user.last_name')
#     skills = SkillSerializer(source='skills', many=True)
#     education = EducationSerializer(source='membereducation_set', many=True)
#     experiences = ExperienceSerializer(source='memberexperience_set', many=True)
#     alumni = Alumni_Serializer(source='alumni_set', many=True)
#     batch = BatchSerializer()
#     course = CourseSerializer()
#     location = LocationSerializer()
#     salutation = SalutationSerializer()

#     class Meta:
#         model = Member
#         fields = '__all__'
