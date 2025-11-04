# api/serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


# ✅ REGISTER SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)
    name = serializers.CharField(write_only=True)
    profession = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('name', 'username', 'email', 'password', 'password2', 'profession')
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        name = validated_data.pop('name', '')
        profession = validated_data.pop('profession', '')
        email = validated_data.get('email')
        username = validated_data.get('username') or email

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data.get('password')
        )
        user.first_name = name
        user.save()

        # Link or update profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.profession = profession
        profile.save()

        return user


# ✅ USER SERIALIZER (For profile or displaying user info)
class UserSerializer(serializers.ModelSerializer):
    profession = serializers.CharField(source='profile.profession', read_only=True)
    name = serializers.CharField(source='first_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'profession')