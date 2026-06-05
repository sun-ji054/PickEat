from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'nickname', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('이미 사용 중인 아이디입니다.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']


class NicknameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']