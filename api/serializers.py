from rest_framework import serializers

from .models import BlockedURL, User, Child


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_parent', 'is_child']


class ChildSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()  # Remove the `source` argument

    class Meta:
        model = Child
        fields = ['id', 'name', 'parent', 'age', 'last_location']

    def get_name(self, obj):  # Ensure the method name follows the pattern "get_<field_name>"
        return f"{obj.user.first_name} {obj.user.last_name}"


class BlockedURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedURL
        fields = ['id', 'parent', 'child', 'url', 'blocked_at']


class ChildLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['latitude', 'longitude', 'last_updated']
