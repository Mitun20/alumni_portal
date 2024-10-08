from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Member_Education, Member_Experience, Alumni, Member, Member_Skills

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  # Adjust field names as needed
        
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

class AlumniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumni
        fields = '__all__'  # Adjust fields as needed

class Alumni_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Alumni
        fields = ['website', 'linked_in', 'twitter_handle', 'address', 'location', 'postal_code', 'registered_on']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member_Skills
        fields = ['skill']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member_Education
        fields = ['institute', 'degree', 'start_year', 'end_year', 'is_currently_pursuing', 'location']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member_Experience
        fields = ['industry', 'role', 'start_date', 'end_date', 'is_currently_working', 'location']
    
    
class MemberDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    skills = SkillSerializer(source='member_skills_set', many=True)
    education = EducationSerializer(source='member_education_set', many=True)
    experiences = ExperienceSerializer(source='member_experience_set', many=True)
    alumni = Alumni_Serializer(source='alumni_set', many=True)  # Include the alumni info

    class Meta:
        model = Member
        fields = '__all__'