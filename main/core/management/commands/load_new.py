from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from main.users.models import User, RegisteredUser
from main.core.models import Currency, EmailServer


class Command(BaseCommand):
	help = "This command to load default domain and subdomains samples into database"
	def add_arguments(self, parser):
		parser.add_argument("--add", action="store_true", dest="add", default=True, help="add default domain only")
	def handle(self, *args, **options):
		if options["add"]:
			emailserver, created = EmailServer.objects.get_or_create(
				server="smtp.yandex.com",
				port=465,
				username="haktiv@supernovasoft.com",
				password="telanbcuukicoqfd", # "Zqw1ia!4FX2s2",
				ssl=True,
				active=True,
			)
			if created:
				print("Default Email Server Added")
			user1, created = User.objects.get_or_create(pk=1)
			if created:
				user1.username = "admin"
				user1.first_name = "Chris"
				user1.last_name = "Daughtry"
				user1.email = "admin@example.com"
				user1.set_password("e8GR2wmasDp8ztKb")
				user1.is_active = True
				user1.is_staff = True
				user1.is_superuser = True
				user1.is_email = True
				user1.is_verified = True
				user1.role = User.ADMIN
				user1.save()
				print("Default User Added")
			user2, created = User.objects.get_or_create(pk=2)
			if created:
				user2.username = "researcher1"
				user2.first_name = "Luwis"
				user2.last_name = "Hammer"
				user2.email = "researcher1@researcher1.com"
				user2.set_password("ZJBkEsSe6jiEyvy")
				user2.is_active = True
				user2.is_staff = False
				user2.is_superuser = False
				user2.is_email = True
				user2.is_verified = True
				user2.role = User.RESEARCHER
				user2.save()
			user3, created = User.objects.get_or_create(pk=3)
			if created:
				user3.username = "customer1"
				user3.first_name = "Ransom"
				user3.last_name = "Jeffry"
				user3.email = "customer1@customer1.com"
				user3.set_password("FhrrJfTqRz(H")
				user3.is_active = True
				user3.is_staff = False
				user3.is_superuser = False
				user3.is_email = True
				user3.is_verified = True
				user3.role = User.CUSTOMER
				user3.save()
			user4, created = User.objects.get_or_create(pk=4)
			if created:
				user4.username = "triage1"
				user4.first_name = "Lisa"
				user4.last_name = "Christopher"
				user4.email = "triage1@triage1.com"
				user4.set_password("NxrJVygzk37a")
				user4.is_active = True
				user4.is_staff = False
				user4.is_superuser = False
				user4.is_email = True
				user4.is_verified = True
				user4.role = User.TRIAGER
				user4.save()
			obj1, created = Currency.objects.get_or_create(
				name="Egyptian Pound",
				code="EG",
				code3="EGP",
				symbol="E£",
				order=1,
			)
			if created:
				print("Default Currency1 Added")
			obj2, created = Currency.objects.get_or_create(
				name="United State Dollar",
				code="US",
				code3="USD",
				symbol="$",
				order=2,
			)
			if created:
				print("Default Currency2 Added")
			obj3, created = Currency.objects.get_or_create(
				name="Euro",
				code="EU",
				code3="EUR",
				symbol="€",
				order=3,
			)
			if created:
				print("Default Currency3 Added")
			researcher_user, created = RegisteredUser.objects.get_or_create(
				first_name="Loana",
				last_name="Voina",
				company_name="",
				password="FifaLenovaRTE$34",
				email="loana.voina@newway2hack.com",
				country="ND",
				role=RegisteredUser.RESEARCHER,
				phone="+20114343335",
				linkedin_profile="https://linkdedin.com/absdefg",
				role_name="Cyber Security Researcher",
			)
			if created:
				print("Default Registration Researcher Added")
			researcher_user, created = RegisteredUser.objects.get_or_create(
				first_name="Nola",
				last_name="Larakas",
				company_name="Brazil Central Bank",
				password="DFGEDfgdrt564Eer",
				email="nola.larakas@example.com",
				country="ND",
				role=RegisteredUser.CUSTOMER,
				phone="+1114343335",
				linkedin_profile="",
				role_name="",
			)
			if created:
				print("Default Registration Customer Added")
			from main.programs.models import ProgramTypeTag, Program
			if not ProgramTypeTag.objects.exists():
				ProgramTypeTag.load_default()
			from main.programs.mock import load_programs
			if not Program.objects.exists():
				load_programs()