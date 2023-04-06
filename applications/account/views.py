from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.account.serializers import RegisterSerializer, ForgotPasswordSerializer, \
    ForgotPasswordConfirmSerializer

User = get_user_model()


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ActivateAPIView(APIView):
    def get(self, request, activation_code):
        user = User.objects.filter(activation_code=activation_code).first()
        if not user:
            return Response({'msg': 'Неверный код активации'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.activation_code = ''
        user.save(update_fields=('is_active', 'activation_code'))
        return Response({'msg': 'Ваш аккаунт успешно активирован'}, status=status.HTTP_200_OK)


class ForgotPasswordAPIVIew(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_code()
        return Response({'msg': 'Вам отправили код активации'}, status=status.HTTP_200_OK)


class ForgotPasswordConfirmAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.change_password()
        return Response({'msg': 'Ваш пароль успешно изменен'}, status=status.HTTP_200_OK)
