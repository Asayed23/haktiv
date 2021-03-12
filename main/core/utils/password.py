import random
import string

from django.apps import apps
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone as djtz
from django.utils.encoding import force_bytes  # , force_text
from django.utils.http import urlsafe_base64_encode  # , urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from password_strength import PasswordStats  # , PasswordPolicy

from main.notify.models import Notification
from main.users.models import PasswordHistory
from .common import get_client_ip, get_city
from .user_agent import get_os
from ..tasks import mail_html_maillist


def password_generator(size=8, chars=string.ascii_letters + string.digits):
    """
    Returns a string of random characters, useful in generating temporary
    passwords for automated password resets.

    size: default=8; override to provide smaller/larger passwords
    chars: default=A-Za-z0-9; override to provide more/less diversity

    Credit: Ignacio Vasquez-Abrams
    Source: http://stackoverflow.com/a/2257449
    """
    return ''.join(random.choice(chars) for i in range(size))


def check_password_policy(password):
    if settings.DEBUG:
        return True, _("OK, Password enabled")
    elif len(settings.PASSWORD_POLICY.test(password)) == 0:
        return True, _("OK, Password Valid")
    elif int(PasswordStats(password=password).strength() * 100) > 36:
        return True, _("OK Password strong and able to use")
    else:
        return False, _("Password is not strong enough")


def reset_password_request(user):
    from main.auth.utils import reset_password_token
    # Accourding to: https://stackoverflow.com/a/13242421/1756032
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.', 1))
    if not isinstance(user, User):
        raise ValueError("Invalid User type")
    res_message, res_code = _("Unknown Error"), 400
    if user is not None:
        token = reset_password_token.make_token(user)
        uid64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        reset_password_link = "%(base_url)s/auth/reset/?new=true&uidb64=%(uidb64)s&token=%(token)s" % dict(
            base_url=settings.FRONTEND_BASE_URL,
            uid64=uid64,
            token=token,
        )
        site_name = settings.FRONTEND_SITE_NAME
        kwargs = dict(
            email=user.email,
            welcome=_("Welcome to %(site_name)s") % dict(site_name=site_name),
            base_url=settings.FRONTEND_BASE_URL,
            reset_password_link=reset_password_link,
            user=dict(
                full_name=user.get_full_name(),
                email=user.email,
            ),
            logo_link=settings.FRONTEND_LOGO_LARGE,
        )
        subject = str(_("%(site_name)s Reset Password")) % dict(site_name=site_name)
        template_name = "users/email/reset.html"
        mail_html_maillist.apply(args=([user.email], subject, template_name, kwargs, settings.LANGUAGE_CODE,))
        res_message, res_code = _("OK, your reset password request has sent"), 200
        notify_user(title=_("Reset Password"), message=res_message, link=None, user=user)
    return res_message, res_code


def change_user_password(user, password, request):
    res_message, res_code = _("Unknown Error"), 400
    for pass_history in PasswordHistory.objects.filter(user=user):
        if check_password(password=password, encoded=pass_history.password):
            return _("Error, you cannot use old password"), 400
    password_policy_state, password_policy_message = check_password_policy(password)
    if password_policy_state:
        user.set_password(password)
        user.save()
        PasswordHistory.objects.create(
            user=user,
            password=make_password(password=password)
        )
        site_url = settings.FRONTEND_BASE_URL
        site_name = settings.FRONTEND_SITE_NAME
        data = dict(
            email=user.email,
            welcome_message=_("Security Alert from %(site_name)s") % dict(site_name=site_name),
            site_url=site_url,
            site_name=site_name,
            ip_address=get_client_ip(request=request),
            city=get_city(request),
            os=get_os(request),
            timestamp=djtz.now(),
            logo_url=settings.FRONTEND_LOGO_LARGE,
        )
        subject = str(_("Password Changed on %(site_name)s")) % dict(site_name=site_name)
        template_name = "core/email/password_changed.html"
        mail_html_maillist.apply(args=([user.email], subject, template_name, data, settings.LANGUAGE_CODE,))
        res_message, res_code = _("OK, Password has changed"), 200
        Notification.notify_user(title=_("Password Changed"), body=_("Your password has been changed successfully"),
                                 user=user)
    return res_message, res_code
