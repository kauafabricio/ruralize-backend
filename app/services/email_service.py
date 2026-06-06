import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""

    def __init__(self, smtp_host: str, smtp_port: int, sender_email: str, sender_password: str, use_tls: bool = True):
        """
        Initialize SMTP configuration

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            sender_email: Email address to send from
            sender_password: Email password or app password
            use_tls: Whether to use TLS encryption
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls

    def send_reward_redemption_email(
        self,
        recipient_email: str,
        user_name: str,
        reward_name: str,
        redemption_code: str,
        pickup_location: str = "Sala 24 - DC Sala Ruralize",
        office_hours: str = "14h - 18h",
        days_valid: int = 7
    ) -> bool:
        """
        Send reward redemption confirmation email

        Args:
            recipient_email: Email address to send to
            user_name: Name of the user
            reward_name: Name of the redeemed reward
            redemption_code: Unique redemption code
            pickup_location: Where to pick up the reward
            office_hours: Office hours for pickup
            days_valid: Number of days valid for pickup

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Calculate pickup deadline
            deadline = datetime.now() + timedelta(days=days_valid)
            deadline_str = deadline.strftime("%d/%m/%Y")

            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Sua recompensa está disponível para resgate"
            message["From"] = self.sender_email
            message["To"] = recipient_email

            # HTML email body
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2ecc71;">Olá, {user_name}.</h2>
                        
                        <p>Seu resgate foi processado com sucesso e sua recompensa já está disponível para retirada.</p>
                        
                        <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #2ecc71; margin: 20px 0;">
                            <p><strong>📦 Recompensa:</strong> {reward_name}</p>
                            <p><strong>📍 Local de Retirada:</strong> {pickup_location}</p>
                            <p><strong>📅 Data para Retirada:</strong> Até {deadline_str}</p>
                            <p><strong>🕒 Horário de Atendimento:</strong> {office_hours}</p>
                            <p><strong>🔑 Código de Resgate:</strong> <code style="background-color: #eee; padding: 2px 5px;">{redemption_code}</code></p>
                        </div>
                        
                        <p style="margin-top: 20px;">Apresente este código juntamente com um documento de identificação no momento da retirada.</p>
                        
                        <p>Caso tenha dúvidas, entre em contato com a equipe Ruralize.</p>
                        
                        <p style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                            Atenciosamente,<br>
                            <strong>Equipe Ruralize</strong><br>
                            <a href="mailto:ruralizecontato@gmail.com">ruralizecontato@gmail.com</a>
                        </p>
                    </div>
                </body>
            </html>
            """

            # Plain text fallback
            text_body = f"""
Olá, {user_name}.

Seu resgate foi processado com sucesso e sua recompensa já está disponível para retirada.

📦 Recompensa: {reward_name}
📍 Local de Retirada: {pickup_location}
📅 Data para Retirada: Até {deadline_str}
🕒 Horário de Atendimento: {office_hours}
🔑 Código de Resgate: {redemption_code}

Apresente este código juntamente com um documento de identificação no momento da retirada.

Caso tenha dúvidas, entre em contato com a equipe Ruralize.

Atenciosamente,
Equipe Ruralize
ruralizecontato@gmail.com
            """

            message.attach(MIMEText(text_body, "plain"))
            message.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info(f"Reward redemption email sent successfully to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    def test_connection(self) -> bool:
        """
        Test SMTP connection

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
            logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
