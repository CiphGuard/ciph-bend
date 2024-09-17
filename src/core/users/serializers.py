from rest_framework import serializers
from .models import CustomUser as User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "is_staff": {"read_only": True},
            "is_superuser": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data["password"]
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return data


# Password Reset
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
