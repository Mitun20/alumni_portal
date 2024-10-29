from rest_framework import serializers
from .models import *

class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = [
            'id',
            'posted_by',
            'job_title',
            'industry',
            'experience_level_from',
            'experience_level_to',
            'location',
            'contact_email',
            'contact_link',
            'role',
            'skills',
            'salary_package',
            'dead_line',
            'job_description',
            'file',
            'post_type',
            'is_active'
        ]

    def to_representation(self, instance):
        # Call the parent class to get the original representation
        representation = super().to_representation(instance)

        # Replace 'file' with its absolute URL if it exists
        if instance.file:
            request = self.context.get('request')
            representation['file'] = request.build_absolute_uri(instance.file.url)

        return representation

class JobPostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = [
            'job_title', 'industry', 'experience_level_from', 'experience_level_to',
            'location', 'contact_email', 'contact_link', 'role', 'salary_package',
            'dead_line', 'job_description', 'post_type', 'skills', 'file'
        ]

    def update(self, instance, validated_data):
        # Handle skills separately if needed
        skills_data = validated_data.pop('skills', None)
        
        # Update the instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if skills_data is not None:
            instance.skills.set(skills_data)

        instance.save()
        return instance

# class BusinessDirectorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BusinessDirectory
#         fields = [
#             'id',
#             'business_name',
#             'description',
#             'website',
#             'industry_type',
#             'location',
#             'contact_email',
#             'contact_number',
#             'country_code',
#             'are_you_part_of_management',
#             'logo',
#         ]
    
#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
        
#         # Build absolute URL for the logo
#         if instance.logo:
#             representation['logo'] = instance.logo.url
#         else:
#             representation['logo'] = None
        
#         return representation
#     def update(self, instance, validated_data):
#         # Update the instance with validated data
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance