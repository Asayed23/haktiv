from django.utils.translation import ugettext as _
from django.conf import settings
from django.core import exceptions
from django.core.validators import RegexValidator, MaxLengthValidator, MinLengthValidator
import django.contrib.auth.password_validation as validators

from rest_framework import serializers
import re

from main.users.models import User


class RegistrationSerializerBase(serializers.Serializer):
    first_name = serializers.CharField(label=_("First Name"), min_length=4, max_length=30,
                                       validators=[RegexValidator(regex=re.compile("[a-zA-Z]+"),
                                                                 message=_("Special Character Not Allowed"))])
    last_name = serializers.CharField(label=_("Last Name"), min_length=4, max_length=30,
                                      validators=[RegexValidator(regex=re.compile("[a-zA-Z]+"),
                                                                message=_("Special Character Not Allowed"))])
    password = serializers.CharField(min_length=8, max_length=40, style={"input_type": "password"})
    # confirm_password = serializers.CharField(min_length=8, max_length=200, style={"input_type": "password"})
    email = serializers.EmailField(max_length=64)
    phone = serializers.RegexField(regex=re.compile("[0-9]+"), max_length=13, min_length=11, help_text=_("Phone number format allowed: +20123456789"))
                                #    validators=[MaxLengthValidator(limit_value=13), _("Max Length 13 digits"),
                                #                MinLengthValidator(limit_value=11), _("Min Length 11 digits")],
                                #           help_text=_("Phone number format allowed: +20123456789"))
    country = serializers.ChoiceField(choices=settings.ALLOWED_COUNTRY_CODE_LIST)

    def validate_email(self, email):
        existing = User.objects.filter(email=email).first()
        if existing:
            raise serializers.ValidationError(_("Someone with that email address has already registered. Was it you?"))
        return email

    def validate(self, data):
        # if not data.get('password') or not data.get('confirm_password'):
        #     raise serializers.ValidationError(dict(password=[_("Please enter a password and confirm it.")]))
        #
        # if data.get('password') != data.get('confirm_password'):
        #     raise serializers.ValidationError(dict(password=[_("Those passwords don't match.")]))
        try:
            # validate the password and catch the exception
            validators.validate_password(password=data.get('password'), user=User)
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(dict(password=list(e.messages)))
        return data


class ResearcherRegistrationSerializer(RegistrationSerializerBase):
    linkedin_profile = serializers.URLField(label=_("LinkedIn Profile"),
                                            help_text=_("Example: https://www.linkedin.com/afadasdf"),
                                            max_length=100)
    def validate(self, data):
        linkedin_regex = re.compile('((http(s?)://)*([a-zA-Z0-9\-])*\.|[linkedin])[linkedin/~\-]+\.[a-zA-Z0-9/~\-_,&=\?\.;]+[^\.,\s<]')
        if not bool(linkedin_regex.match(data.get("linkedin_profile"))):
            raise serializers.ValidationError(dict(linkedin_profile=[_("Your LinkedIn Profile does not match")]))

        return super(ResearcherRegistrationSerializer, self).validate(data)

        
class CompanyRegistrationSerializer(RegistrationSerializerBase):
    company_name = serializers.CharField(label=_("Company Name"), min_length=4, max_length=40,
                                         validators=[RegexValidator(regex=re.compile("[a-zA-Z]+"),
                                                                 message=_("Special Character Not Allowed"))])
    role_name = serializers.CharField(label=_("Your Role"), min_length=4, max_length=40,
                                      validators=[RegexValidator(regex=re.compile("[a-zA-Z]+"),
                                                                 message=_("Special Character Not Allowed"))])