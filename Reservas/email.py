from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_reservation_created_notification(reservation):
    try:
        if not reservation.created_by or not reservation.created_by.correo:
            return False

        subject = f'Reserva creada - {reservation.area.nombre}'

        context = {
            'reserva': reservation,
            'usuario': reservation.created_by,
            'area': reservation.area,
            'site_name': 'LAMBDA Residencial',
            'reserva_url': f"{settings.FRONTEND_URL}/reservas/{reservation.id}",
        }

        html_message = render_to_string('emails/reservation_created.html', context)
        plain_message = render_to_string('emails/reservation_created.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.created_by.correo],
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception as e:
        print(f"Error enviando notificación de reserva creada: {e}")
        return False


def send_reservation_approved_notification(reservation):
    try:
        if not reservation.created_by or not reservation.created_by.correo:
            return False

        subject = f'Reserva aprobada - {reservation.area.nombre}'

        context = {
            'reserva': reservation,
            'usuario': reservation.created_by,
            'area': reservation.area,
            'approved_by': reservation.approved_by,
            'site_name': 'LAMBDA Residencial',
            'reserva_url': f"{settings.FRONTEND_URL}/reservas/{reservation.id}",
        }

        html_message = render_to_string('emails/reservation_approved.html', context)
        plain_message = render_to_string('emails/reservation_approved.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.created_by.correo],
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception as e:
        print(f"Error enviando notificación de reserva aprobada: {e}")
        return False


def send_reservation_rejected_notification(reservation):
    try:
        if not reservation.created_by or not reservation.created_by.correo:
            return False

        subject = f'Reserva rechazada - {reservation.area.nombre}'

        context = {
            'reserva': reservation,
            'usuario': reservation.created_by,
            'area': reservation.area,
            'approved_by': reservation.approved_by,
            'site_name': 'LAMBDA Residencial',
            'reserva_url': f"{settings.FRONTEND_URL}/reservas/{reservation.id}",
        }

        html_message = render_to_string('emails/reservation_rejected.html', context)
        plain_message = render_to_string('emails/reservation_rejected.txt', context)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reservation.created_by.correo],
            html_message=html_message,
            fail_silently=False,
        )

        return bool(result)

    except Exception as e:
        print(f"Error enviando notificación de reserva rechazada: {e}")
        return False
