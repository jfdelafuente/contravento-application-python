"""
Email sending utilities with async SMTP support.

Provides functions for sending transactional emails (verification, password reset)
with Spanish templates.
"""

import logging
from typing import List, Optional

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import settings


logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
) -> bool:
    """
    Send an email asynchronously.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body_text: Plain text email body
        body_html: Optional HTML email body

    Returns:
        True if email sent successfully, False otherwise

    Example:
        >>> await send_email(
        ...     "user@example.com",
        ...     "Test Email",
        ...     "This is a test email"
        ... )
        True
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = settings.smtp_from
        message["To"] = to_email
        message["Subject"] = subject

        # Add plain text part
        text_part = MIMEText(body_text, "plain", "utf-8")
        message.attach(text_part)

        # Add HTML part if provided
        if body_html:
            html_part = MIMEText(body_html, "html", "utf-8")
            message.attach(html_part)

        # Send email
        if settings.is_testing or settings.is_development:
            # In dev/test, just log the email
            logger.info(
                f"[EMAIL] To: {to_email}, Subject: {subject}\n"
                f"Body:\n{body_text}"
            )
            return True

        # Production: send via SMTP
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user if settings.smtp_user else None,
            password=settings.smtp_password if settings.smtp_password else None,
            use_tls=settings.smtp_tls,
        )

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_verification_email(to_email: str, username: str, token: str) -> bool:
    """
    Send email verification message.

    Args:
        to_email: Recipient email address
        username: User's username
        token: Verification token

    Returns:
        True if email sent successfully

    Example:
        >>> await send_verification_email(
        ...     "maria@example.com",
        ...     "maria_garcia",
        ...     "verification_token_here"
        ... )
        True
    """
    # TODO: Update with actual frontend URL when available
    verification_url = f"http://localhost:3000/verify-email?token={token}"

    subject = "Verifica tu cuenta en ContraVento"

    body_text = f"""
Hola {username},

Gracias por registrarte en ContraVento, la plataforma social para ciclistas.

Para completar tu registro, por favor verifica tu cuenta haciendo clic en el siguiente enlace:

{verification_url}

Este enlace expira en 24 horas.

Si no creaste esta cuenta, puedes ignorar este correo.

¡Nos vemos en la ruta!
Equipo ContraVento

---
Este es un mensaje automático, por favor no respondas a este correo.
"""

    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>¡Bienvenido a ContraVento, {username}!</h2>
        <p>Gracias por registrarte en ContraVento, la plataforma social para ciclistas.</p>
        <p>Para completar tu registro, por favor verifica tu cuenta:</p>
        <a href="{verification_url}" class="button">Verificar mi cuenta</a>
        <p>O copia y pega este enlace en tu navegador:</p>
        <p style="word-break: break-all;">{verification_url}</p>
        <p><strong>Este enlace expira en 24 horas.</strong></p>
        <p>Si no creaste esta cuenta, puedes ignorar este correo.</p>
        <p>¡Nos vemos en la ruta!</p>
        <p>Equipo ContraVento</p>
        <div class="footer">
            <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
        </div>
    </div>
</body>
</html>
"""

    return await send_email(to_email, subject, body_text, body_html)


async def send_password_reset_email(to_email: str, username: str, token: str) -> bool:
    """
    Send password reset email.

    Args:
        to_email: Recipient email address
        username: User's username
        token: Password reset token

    Returns:
        True if email sent successfully

    Example:
        >>> await send_password_reset_email(
        ...     "maria@example.com",
        ...     "maria_garcia",
        ...     "reset_token_here"
        ... )
        True
    """
    # TODO: Update with actual frontend URL when available
    reset_url = f"http://localhost:3000/reset-password?token={token}"

    subject = "Restablece tu contraseña - ContraVento"

    body_text = f"""
Hola {username},

Recibimos una solicitud para restablecer tu contraseña en ContraVento.

Para crear una nueva contraseña, haz clic en el siguiente enlace:

{reset_url}

Este enlace expira en 1 hora.

Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.
Tu contraseña actual permanecerá sin cambios.

Saludos,
Equipo ContraVento

---
Este es un mensaje automático, por favor no respondas a este correo.
"""

    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #FF9800;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .warning {{
            background-color: #FFF3CD;
            border-left: 4px solid #FFC107;
            padding: 12px;
            margin: 20px 0;
        }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Restablecer contraseña</h2>
        <p>Hola {username},</p>
        <p>Recibimos una solicitud para restablecer tu contraseña en ContraVento.</p>
        <p>Para crear una nueva contraseña, haz clic en el botón:</p>
        <a href="{reset_url}" class="button">Restablecer contraseña</a>
        <p>O copia y pega este enlace en tu navegador:</p>
        <p style="word-break: break-all;">{reset_url}</p>
        <div class="warning">
            <strong>⚠️ Este enlace expira en 1 hora.</strong>
        </div>
        <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este correo.
        Tu contraseña actual permanecerá sin cambios.</p>
        <p>Saludos,<br>Equipo ContraVento</p>
        <div class="footer">
            <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
        </div>
    </div>
</body>
</html>
"""

    return await send_email(to_email, subject, body_text, body_html)
