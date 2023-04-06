from decouple import config
from django.core.mail import send_mail


def send_activation_link(email, activation_code):
    full_link = f'http://localhost:8000/api/v1/account/activate/{activation_code}'
    send_mail(
        'Ссылка активации',
        full_link,
        config('EMAIL_HOST_USER'),
        [email]
    )


def send_activation_code(email, activation_code):
    send_mail(
        'Пароль активации',
        activation_code,
        config('EMAIL_HOST_USER'),
        [email],
    )
