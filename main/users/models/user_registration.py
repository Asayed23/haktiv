from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from main.core.tasks import mail_html_maillist
from main.core.models import TimeStampedModel
from main.users.models import User

class RegisteredUser(TimeStampedModel):
    class Meta:
        verbose_name = _("Registered User")
        verbose_name_plural = _("Registered Users")

    COUNTRIES = (
        ("EG", _("Egypt"),),
        ("ND", _("Other"),),
    )

    RESEARCHER = "researcher"
    CUSTOMER = "customer"

    ROLES = (
        (RESEARCHER, _("Researcher"),),
        (CUSTOMER, _("Customer"),),
    )

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUSES = (
        (PENDING, _("Pending")),
        (APPROVED, _("Approved")),
        (REJECTED, _("Rejected")),
    )

    first_name = models.CharField(_("First Name"), max_length=20,)
    last_name = models.CharField(_("Last Name"), max_length=20,)
    company_name = models.CharField(_("Company Name"), max_length=20, blank=True)
    password = models.CharField(_("Password"), max_length=40,)
    email = models.EmailField(_("Email Address"), max_length=64, unique=True)
    country = models.CharField(_("Country"), max_length=2, default="EG", choices=COUNTRIES)
    role = models.CharField(_("Role"), max_length=10, default=RESEARCHER, choices=ROLES)
    status = models.CharField(_("Status"), max_length=20, default=PENDING, choices=STATUSES)
    phone = models.CharField(verbose_name=_("Phone Number"), max_length=15, blank=True,)
    linkedin_profile = models.URLField(verbose_name=_("LinkedIn Profile"), max_length=100, blank=True)
    bio = models.TextField(_("BIO"), blank=True)
    role_name = models.CharField(verbose_name=_("Role Name"), max_length=40, blank=True)

    @property
    def display_password(self):
        return f"{self.password[:2]}******"
    # display_password.short_description = _("Password")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    # full_name.short_description = _("Full Name")

    def approve_user(self, message=None):
        from main.core.utils import password_generator
        if not User.objects.filter(email=self.email).exists():
            register_template = "users/email/new_registration_your_account_approved.html"
            params = dict(
                registered_name=self.full_name,
                message=message,
            )
            mail_html_maillist(maillist=[self.email], subject=_("Your account has been Approved"),
                               html_template=register_template, kwargs=params,
                               lang=settings.LANGUAGE_CODE)
            
            User.objects.create_user(
                username=password_generator(size=10),
                password=self.password,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                company_name=self.company_name,
                phone=self.phone,
                bio=self.bio,
                role=User.CUSTOMER if self.role == self.CUSTOMER else User.RESEARCHER,
            )
        else:
            raise ValidationError(_("User already registered"))

    def reject_user(self, message=None):
        register_template = "users/email/new_registration_your_account_rejected.html"
        params = dict(
            registered_name=self.full_name,
            message=message,
        )
        mail_html_maillist(maillist=[self.email], subject=_("Your account has been Rejected"),
                           html_template=register_template, kwargs=params,
                           lang=settings.LANGUAGE_CODE)

    def send_welcome_mail_to_new_registration(self):
        admin_template = "users/email/new_registration_inform_admin.html"
        register_template = "users/email/new_registration_welcome_on_board.html"
        admins = User.objects.filter(is_superuser=True, is_staff=True, is_active=True, role=User.ADMIN)
        mail_html_maillist(maillist=[user.email for user in admins], subject=_("New Registration on the Board"),
                           html_template=admin_template, kwargs=dict(registered_name=self.full_name()),
                           lang=settings.LANGUAGE_CODE)
        mail_html_maillist(maillist=[self.email], subject=_("Welcome on the Board"),
                           html_template=register_template, kwargs=dict(registered_name=self.full_name()),
                           lang=settings.LANGUAGE_CODE)

    def __str__(self):
        return self.full_name