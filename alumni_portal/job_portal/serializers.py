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

class BusinessDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDirectory
        fields = [
            'id',
            'business_name',
            'description',
            'website',
            'industry_type',
            'location',
            'contact_email',
            'contact_number',
            'country_code',
            'are_you_part_of_management',
            'logo',
            'listed_on',
            'listed_by',
        ]

    def to_representation(self, instance):
        # Call the parent class to get the original representation
        representation = super().to_representation(instance)

        # Replace 'logo' with its absolute URL if it exists
        if instance.logo:
            request = self.context.get('request')
            representation['logo'] = request.build_absolute_uri(instance.logo.url)

        return representation