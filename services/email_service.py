import os
import resend
from pathlib import Path

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@ceready.co.uk")

def send_evidence_pack_email(to_email: str, company_name: str, zip_path: str) -> bool:
    """Send evidence pack ZIP as email attachment after payment."""
    try:
        with open(zip_path, "rb") as f:
            zip_bytes = f.read()

        filename = f"CyberGuard_EvidencePack_{company_name.replace(' ', '_')}.zip"

        params = {
            "from": f"CyberGuard Essentials <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": f"Your CyberGuard Evidence Pack — {company_name}",
            "html": f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #0a0a0f; color: #ffffff; padding: 40px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <h1 style="color: #00c2cb; font-size: 24px;">Your Evidence Pack is Ready</h1>
    <p style="color: #aaaaaa;">Thank you for your purchase. Please find your Cyber Essentials Evidence Pack attached.</p>
    
    <div style="background: #12121a; border: 1px solid rgba(0,194,203,0.3); border-radius: 8px; padding: 24px; margin: 24px 0;">
      <h2 style="color: #ffffff; font-size: 16px; margin-top: 0;">What's included:</h2>
      <ul style="color: #aaaaaa; line-height: 1.8;">
        <li>Information Security Policy</li>
        <li>Access Control Policy</li>
        <li>Patch Management Policy</li>
        <li>Malware Protection Policy</li>
        <li>Network Security Policy</li>
        <li>Incident Response Policy</li>
        <li>Cyber Essentials Compliance Statement</li>
      </ul>
    </div>

    <p style="color: #aaaaaa;">These documents are pre-filled with <strong style="color: #ffffff;">{company_name}</strong>'s details and aligned to NCSC Cyber Essentials v3.3.</p>
    
    <p style="color: #aaaaaa;">To get certified, submit your self-assessment via an IASME-licensed certification body at <a href="https://iasme.co.uk" style="color: #00c2cb;">iasme.co.uk</a>. Basic certification starts from £320+VAT.</p>

    <hr style="border: 1px solid #1a1a2e; margin: 32px 0;">
    <p style="color: #666; font-size: 12px;">CyberGuard Essentials by Corvaxis Ltd · <a href="https://ceready.co.uk" style="color: #00c2cb;">ceready.co.uk</a></p>
  </div>
</body>
</html>
            """,
            "attachments": [
                {
                    "filename": filename,
                    "content": zip_bytes,
                }
            ],
        }

        resend.Emails.send(params)
        return True

    except Exception as e:
        print(f"Email send failed: {e}")
        return False


def send_payment_receipt_email(to_email: str, company_name: str, amount: str = "£9.99") -> bool:
    """Send payment receipt email."""
    try:
        params = {
            "from": f"CyberGuard Essentials <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": f"Payment Receipt — CyberGuard Evidence Pack",
            "html": f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #0a0a0f; color: #ffffff; padding: 40px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <h1 style="color: #00c2cb; font-size: 24px;">Payment Receipt</h1>
    
    <div style="background: #12121a; border: 1px solid rgba(0,194,203,0.3); border-radius: 8px; padding: 24px; margin: 24px 0;">
      <table style="width: 100%; color: #aaaaaa;">
        <tr><td>Product</td><td style="text-align: right; color: #fff;">CyberGuard Evidence Pack</td></tr>
        <tr><td>Organisation</td><td style="text-align: right; color: #fff;">{company_name}</td></tr>
        <tr><td>Amount paid</td><td style="text-align: right; color: #00c2cb; font-weight: bold;">{amount}</td></tr>
        <tr><td>Standard</td><td style="text-align: right; color: #fff;">NCSC Cyber Essentials v3.3</td></tr>
      </table>
    </div>

    <p style="color: #aaaaaa;">Your evidence pack has been sent in a separate email. Please check your inbox.</p>
    
    <hr style="border: 1px solid #1a1a2e; margin: 32px 0;">
    <p style="color: #666; font-size: 12px;">CyberGuard Essentials by Corvaxis Ltd · <a href="https://ceready.co.uk" style="color: #00c2cb;">ceready.co.uk</a></p>
  </div>
</body>
</html>
        """,
        }

        resend.Emails.send(params)
        return True

    except Exception as e:
        print(f"Receipt email failed: {e}")
        return False
