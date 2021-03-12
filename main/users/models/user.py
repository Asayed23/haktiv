# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.db.models import Max

from main.core.models import TimeStampedModel
from main.users.manager import UserManager

import pytz, os, random
import pyotp

username_validator = ASCIIUsernameValidator()
_PHONE_REGEX   = RegexValidator(regex=r'(\d{9,15})$', message=_("Your phone number should consist of 9-15 digits. Example: 1114442277"))

class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
	"""
Haktiv has 4 types of personas:
# Customer:
	Shall be our targeted clients, who would register to add a program & request from Haktiv team to start allocating researchers for it
# Researcher:
	Shall be our freelance hackers, who would register to be part of Haktiv team and shall got through a defined interviewing process to join our hackers community & start working on customer’s programs
# Triager:
	The main goal of Haktiv product is to take over the communication between customer & researcher
	So Haktiv shall have a team of professional triagers who would be responsible for verifying the process of program submit done by customers, allocating researcher to work on it & verify reports submitted by researchers before being sent to customers
	Their main goal would be: Ensuring the quality & Monitoring the end to end cycle is between customer & researcher with no needed direct communication between them
	Accordingly, from customer’s &  researcher’s  perspective; the whole process of program creation, report submission & payment would be automated & digitalized without any human intervention from their sides
# Admin:
Admin should be the one responsible for:
	User management
	Manage interviewing process for hackers & triagers
	Customers program management
	Configure & monitor workflow for platform programs & reports submission
	Payout management
	Reporting & Statistics for hackers progress, programs status & earnings
"""
	class Meta:
		verbose_name = _("User")
		verbose_name_plural = _("Users")
		swappable = 'AUTH_USER_MODEL'

	ADMIN 	   = "ADMIN"
	TRIAGER    = "TRIAGER"
	RESEARCHER = "RESEARCHER"
	CUSTOMER   = "CUSTOMER"

	ROLES = (
		(ADMIN, _("Admin"),),
		(TRIAGER, _("Triager"),),
		(RESEARCHER, _("Researcher"),),
		(CUSTOMER, _("Customer"),),
	)
	# Contact Info
	email 					= models.EmailField(_('Email address'), unique=True)
	secondary_email 		= models.EmailField(_('Secondary Email address'), null=True, blank=True)
	phone           	    = models.CharField(verbose_name=_("Phone Number"), max_length=15, blank=True, validators=[_PHONE_REGEX])
	username 	= models.CharField(_('Username'), max_length=150, unique=True,
		help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
		validators=[username_validator],
		error_messages={
			'unique': _("A user with that username already exists."),
		},
	)

	# Personal Info
	company_name    = models.CharField(_("Company Name"), max_length=50, default="", blank=True, null=True)
	first_name 		= models.CharField(_('First name'), max_length=30, default="", blank=True, null=True)
	last_name 		= models.CharField(_('Last name'), max_length=30, default="", blank=True, null=True)
	birthdate 		= models.DateField(verbose_name=_("Birth Date"), null=True, blank=True)
	home_address 	= models.TextField(verbose_name=_("Home"), blank=True)
	avatar 		    = models.ImageField(verbose_name=_("Avatar"), upload_to=settings.DEFAULT_USER_FOLDER, blank=True,
										  default=settings.DEFAULT_USER_AVATAR)
	bio				= models.TextField(_("BIO"), blank=True)
	title			= models.CharField(_("Title"), max_length=100, blank=True)

	# Permissions
	role     		= models.CharField(_("User Role"), max_length=50, default=RESEARCHER, choices=ROLES)
	is_staff 		= models.BooleanField(_('Is Staff'), default=False)
	is_active 		= models.BooleanField(_('Is Active'), default=False)
	is_verified 	= models.BooleanField(_('Is Verified'), default=False)
	is_email    	= models.BooleanField(_('Is Email Verified'), default=False)
	has_2fa 		= models.BooleanField(_("Has Two Factor Auth."), default=False)
	otp_key         = models.CharField(_("OTP Key"), null=True , blank=True, max_length=256)

	objects = UserManager()
	EMAIL_FIELD = 'email'
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']

	def date_joined(self):
		return self.created
	date_joined.short_description = _("Join Date")

	def get_full_name(self):
		"""
		Returns the first_name plus the last_name, with a space in between.
		"""
		full_name = '%s %s' % (self.first_name, self.last_name) if self.first_name and self.last_name else self.username
		return full_name.strip()
	get_full_name.short_description = _("Full Name")
	
	@property
	def fullname(self):
		return self.get_full_name()

	def get_short_name(self):
		"Returns the short name for the user."
		return f"{self.first_name} {self.last_name[:1]}." if self.first_name and self.last_name else self.username
	get_short_name.short_description = _("Short Name")

	def __str__(self):
		return self.get_full_name()

	def get_next_id(self):
		id_max = User.objects.aggregate(Max('id'))["id__max"]
		return id_max + 1 if id_max else 1

	def save(self, *args, **kwargs):
		if self.pk:
			if self.has_2fa:
				self.otp_key = pyotp.random_base32()
		else:
			self.pk = self.get_next_id()
		super(User, self).save(*args, **kwargs)

	def is_password_expired(self):
		from .password_history import PasswordHistory
		last_password = PasswordHistory.objects.filter(user=self).last()
		return last_password and int(settings.PASSWORD_EXPIRE_DAYS) < int(last_password.since_days())

	def get_social_media(self):
		from .user_social_media import UserSocialMedia
		return UserSocialMedia.objects.filter(user=self)
