from rest_framework import serializers

from .models import BlockedURL, User, Child


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_parent', 'is_child']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'user', 'parent', 'last_location']


class BlockedURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedURL
        fields = ['id', 'parent', 'child', 'url', 'blocked_at']


class ChildLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['latitude', 'longitude', 'last_updated']
