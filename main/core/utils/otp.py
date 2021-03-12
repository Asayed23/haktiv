from django.conf import settings

from main.users.models import User
import pyotp

def create_key() -> str:
    """
    Create new random key
    :returns: Random secret
    :rtype: str
    """
    return pyotp.random_base32(length=20)

def create_otp_code(key: str):
    """
    Create new OTP code from key.
    :param key:
    :return: OTP code
    """
    return pyotp.TOTP(key).now()

def check_key_otp(key: str, otp: object):
    """
    Check current token is match secret otp digits
    :param otp:
    :return:
    """
    otp = int(otp) if isinstance(otp, str) or isinstance(otp, object) else otp
    return pyotp.TOTP(key,).verify(otp=otp)

def create_qr_link(key, user):
    """
    Create QR link to set application OTP.
    :param key:  Key used to generate OTP
    :type key: str
    :param user: User that link should be created for
    :type user: User
    :return: Link to generated QR code from backend
    :rtype: str
    """
    totp = pyotp.TOTP(key)
    return totp.provisioning_uri((
        getattr(user, User.USERNAME_FIELD),
        settings.STAGE2_AUTH["APPLICATION_ISSUER_NAME"],
    ))

def check_twofactor(request):
    token = None