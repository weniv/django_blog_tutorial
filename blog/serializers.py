from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__' # ['title', 'content', 'created_at', 'updated_at', 'is_public', 'file_upload', 'category', 'tags']