from django.db import models
from django.contrib.auth.models import User
import pyotp
import qrcode
import io
import base64
from django.conf import settings


class TwoFactorAuth(models.Model):
    """Model to store user's 2FA secret and verification status"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="twofa")
    secret_key = models.CharField(max_length=32, unique=True)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"2FA for {self.user.email}"

    def generate_secret(self):
        """Generate a new secret key for TOTP"""
        self.secret_key = pyotp.random_base32()
        return self.secret_key

    def get_qr_code_url(self):
        """Generate QR code URL for authenticator app setup"""
        totp = pyotp.TOTP(self.secret_key)
        provisioning_uri = totp.provisioning_uri(
            name=self.user.email,
            issuer_name=getattr(settings, "TWOFA_ISSUER_NAME", "Finance Tracker"),
        )
        return provisioning_uri

    def generate_qr_code(self):
        """Generate QR code image as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_qr_code_url())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

    def verify_token(self, token):
        """Verify the provided TOTP token"""
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token, valid_window=1)

    def generate_backup_codes(self, count=10):
        """Generate backup codes for emergency access"""
        import secrets

        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append(code)
        self.backup_codes = codes
        return codes

    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        code_upper = code.upper()
        # Create a new list without the used code
        new_backup_codes = []
        found = False

        for backup_code in self.backup_codes:
            if backup_code.upper() == code_upper and not found:
                found = True
                # Skip this code (consume it)
            else:
                new_backup_codes.append(backup_code)

        if found:
            self.backup_codes = new_backup_codes
            self.save()
            return True
        return False

    class Meta:
        verbose_name = "Two Factor Authentication"
        verbose_name_plural = "Two Factor Authentications"
