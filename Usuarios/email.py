from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

def send_welcome_email(user):

    try:
        subject = 'Bienvenido a LAMBDA Residencial'

        context = {
            'user': user,
            'site_name': 'LAMBDA Residencial',
            'login_url': f"{settings.FRONTEND_URL}/login",
        }

        html_message = render_to_string('emails/welcome.html', context)
        plain_message = render_to_string('emails/welcome.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.correo],
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception as e:
        print(f"Error enviando email de bienvenida: {e}")
        return False

def send_password_reset_email(user, reset_token):
    
    try:
        subject = 'Recuperación de contraseña - LAMBDA Residencial'

        # URL completa para el reset
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'LAMBDA Residencial',
            'valid_hours': 2, 
        }

        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.correo],
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception:
        return False

def send_password_changed_notification(user):

    try:
        subject = 'Contraseña actualizada - LAMBDA Residencial'

        context = {
            'user': user,
            'site_name': 'LAMBDA Residencial',
            'timestamp': timezone.now().strftime('%d/%m/%Y a las %H:%M:%S %Z'),
        }

        html_message = render_to_string('emails/password_changed.html', context)
        plain_message = render_to_string('emails/password_changed.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.correo],
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception:
        return False