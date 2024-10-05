from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Member_Education
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