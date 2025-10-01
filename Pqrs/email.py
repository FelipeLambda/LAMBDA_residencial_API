from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.db.models import Q

Usuario = get_user_model()


def send_pqrs_created_notification(pqrs):
    try:
        admins = Usuario.objects.filter(
            Q(groups__permissions__codename='respond_pqrs') | Q(is_superuser=True)
        ).distinct()

        if not admins.exists():
            return False

        admin_emails = [admin.correo for admin in admins if admin.correo]

        if not admin_emails:
            return False

        subject = f'Nueva {pqrs.get_tipo_display()} - {pqrs.asunto}'

        context = {
            'pqrs': pqrs,
            'usuario': pqrs.usuario,
            'tipo': pqrs.get_tipo_display(),
            'site_name': 'LAMBDA Residencial',
            'admin_url': f"{settings.FRONTEND_URL}/admin/pqrs/{pqrs.id}",
        }

        html_message = render_to_string('emails/pqrs_created.html', context)
        plain_message = render_to_string('emails/pqrs_created.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception as e:
        print(f"Error enviando notificación de PQRS creada: {e}")
        return False


def send_pqrs_response_notification(pqrs):
    try:
        if not pqrs.usuario or not pqrs.usuario.correo:
            return False

        subject = f'Respuesta a tu {pqrs.get_tipo_display()} - {pqrs.asunto}'

        context = {
            'pqrs': pqrs,
            'usuario': pqrs.usuario,
            'tipo': pqrs.get_tipo_display(),
            'respondido_por': pqrs.respondido_por,
            'site_name': 'LAMBDA Residencial',
            'pqrs_url': f"{settings.FRONTEND_URL}/pqrs/{pqrs.id}",
        }

        html_message = render_to_string('emails/pqrs_response.html', context)
        plain_message = render_to_string('emails/pqrs_response.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[pqrs.usuario.correo],
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception as e:
        print(f"Error enviando notificación de respuesta PQRS: {e}")
        return False
