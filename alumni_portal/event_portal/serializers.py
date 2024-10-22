from rest_framework import serializers
from .models import *


class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.title', read_only=True)
    posted_by_full_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    event_wallpaper = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'

    def get_event_wallpaper(self, obj):
        request = self.context.get('request')
        if obj.event_wallpaper:
            return request.build_absolute_uri(obj.event_wallpaper.url)
        return None  # or return a default URL if needed
        # fields = ['id', 'title', 'category_name', 'posted_by_full_name', ...]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

