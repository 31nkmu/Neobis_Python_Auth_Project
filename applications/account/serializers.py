from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.account.tasks import send_activation_link, send_activation_code

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


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'msg': 'Нет такого пользователя'})
        return email

    def send_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        user.save(update_fields=('activation_code',))
        send_activation_code(email=email, activation_code=user.activation_code)


class ForgotPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, max_length=128, min_length=6)
    new_password_confirm = serializers.CharField(max_length=128, min_length=6, write_only=True, required=True)
    activation_code = serializers.CharField(max_length=128, required=True, write_only=True)

    def validate(self, attrs):
        p1 = attrs.get('new_password')
        p2 = attrs.pop('new_password_confirm')
        if p1 != p2:
            raise serializers.ValidationError({'msg': 'Пароли не совпадают'})
        email = attrs.get('email')
        activation_code = attrs.get('activation_code')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'msg': 'Нет такого пользователя'})
        if not User.objects.filter(activation_code=activation_code, email=email).exists():
            raise serializers.ValidationError({'msg': 'Неверный активационный код'})
        return attrs

    def change_password(self):
        email = self.validated_data.get('email')
        activation_code = self.validated_data.get('activation_code')
        password = self.validated_data.get('new_password')
        user = User.objects.get(email=email, activation_code=activation_code)
        user.set_password(password)
        user.activation_code = ''
        user.save(update_fields=('activation_code', 'password'))


