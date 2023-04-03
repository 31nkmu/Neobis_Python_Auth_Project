from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.account.tasks import send_activation_link

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')

    def validate(self, attrs):
        p1 = attrs.get('password')
        p2 = attrs.pop('password2')
        if len(p1) < 6:
            raise serializers.ValidationError({'msg': 'Пароль должен быть не менее 6 символов'})
        if p1 != p2:
            raise serializers.ValidationError({'msg': 'Пароли не совпадают'})
        return attrs

    @staticmethod
    def validate_email(email):
        if User.objects.filter(email=email):
            raise serializers.ValidationError({'msg': 'Такой пользователь уже существует'})
        return email

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        send_activation_link(email=validated_data.get('email'), activation_code=user.activation_code)
        return user
