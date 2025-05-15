from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        read_only_fields = ['parent']


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_parent', 'is_child']


class ChildCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', write_only=True)
    password = serializers.CharField(write_only=True)

    user = UserPublicSerializer(read_only=True)  # Nested child user data
    parent = UserPublicSerializer(read_only=True)  # Nested parent data

    class Meta:
        model = Child
        fields = ['id', 'username', 'password', 'age', 'last_location', 'user', 'parent']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        user = User.objects.create(
            username=user_data['username'],
            is_child=True,
            is_parent=False,
            password=make_password(password)
        )
        parent = self.context['request'].user
        child = Child.objects.create(user=user, parent=parent, **validated_data)
        return child


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to the token response
        user = self.user
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_parent': user.is_parent,
        }

        # If the user is a child, include child-specific data
        if user.is_child:
            child = Child.objects.get(user=user)  # Get the related child data
            user_data['child'] = {
                'id': child.id,
                'age': child.age,
                'last_location': child.last_location
            }

        data['user'] = user_data

        return data



class URLCheckSerializer(serializers.Serializer):
    url = serializers.URLField()
    child_id = serializers.IntegerField()
