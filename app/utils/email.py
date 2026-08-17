import resend
from app.config import get_settings

settings = get_settings()

resend.api_key = settings.RESEND_API_KEY

def send_otp_email(to_email: str, otp_code: str, subject: str = "Your Verification Code"):
    """
    Sends an OTP email using Resend.
    """
    try:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Brand Bridge</h2>
            <p>Your Verification Code is:</p>
            <h1 style="color: #4CAF50; font-size: 32px; letter-spacing: 5px;">{otp_code}</h1>
            <p>This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.</p>
            <p>If you did not request this, please ignore this email.</p>
        </div>
        """
        
        response = resend.Emails.send({
            "from": settings.FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        })
        
        print(f"📧 Resend Email Sent! ID: {response.get('id')} to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email via Resend: {e}")
        return False
