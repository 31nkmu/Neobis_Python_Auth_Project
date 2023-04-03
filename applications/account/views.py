from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.account.serializers import RegisterSerializer

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
