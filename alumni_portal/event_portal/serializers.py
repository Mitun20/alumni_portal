from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title', read_only=True)
    posted_by_full_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        # fields = ['id', 'title', 'category_name', 'posted_by_full_name', ...]
