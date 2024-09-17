import os
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from core.emails import send_html_email
from core.utils.response import response_with_detail
from .tokens import account_activation_token
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer,
)
from .models import CustomUser as User
from rest_framework.response import Response


class UserRegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetailView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class ChangePasswordView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.data.get("old_password")):
            return response_with_detail(
                status_code=status.HTTP_400_BAD_REQUEST, message="Contraseña incorrecta."
            )

        if serializer.data.get("old_password") == serializer.data.get("new_password"):
            return response_with_detail(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="La nueva contraseña no puede ser igual a la anterior.",
            )

        user.set_password(serializer.data.get("new_password"))
        user.save()
        return response_with_detail("La contraseña se cambió con éxito.")


class PasswordResetView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            self._send_reset_email(user)
        except User.DoesNotExist:
            pass

        return response_with_detail("Correo electrónico enviado")

    @staticmethod
    def _send_reset_email(user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        reset_link = f"{os.getenv('FRONTEND_RECOVER_URL', '')}/?uid={uid}&token={token}"
        send_html_email(
            "Restablecer contraseña",
            user.email,
            "emails/auth/password_reset.html",
            {
                "user": user,
                "reset_link": reset_link,
            },
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def post(self, request, uid, token, *args, **kwargs):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_user_by_id(uid)
        if user is None:
            return response_with_detail("Usuario inválido", status_code=status.HTTP_400_BAD_REQUEST)

        if not account_activation_token.check_token(user, token):
            return response_with_detail("Token inválido", status_code=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data["new_password"])
        user.save()

        return response_with_detail("Contraseña restablecida")

    @staticmethod
    def get_user_by_id(uid):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
