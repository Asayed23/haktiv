import glob, os

from django.core.management import BaseCommand
from django.db import connection

class Command(BaseCommand):
	help = "Removes all migrations"
	app_directory = "main"

	def handle(self, *args, **options):
		try:
			for filename in glob.iglob("{0}/**/migrations/*.py".format(self.app_directory) if os.name == 'nt' else \
									   "{0}\\**\\migrations\\*.py".format(self.app_directory)):
				if all((filename.split("/")[-1] != "__init__.py", filename.split("\\")[-1] != "__init__.py",)):
					os.remove(filename)
			print("Migration files removed.")
		except OSError:
			print("Migration files may not exist.")
		try:
			''' Drops all tables and sequences from a postgres database '''
			sequence_sql = '''SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema='public' '''

			table_sql = " SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type != 'VIEW'"
			with connection.cursor() as cursor:
				cursor.execute(table_sql)
				rows = cursor.fetchall()
				for row in rows:
					try:
						cursor.execute('drop table %s cascade ' % row[0])
						print("dropping table %s" % row[0])
					except:
						print("couldn't drop table %s" % row[0])
				cursor.execute(sequence_sql)
				rows = cursor.fetchall()
				for row in rows:
					try:
						cursor.execute('DROP SEQUENCE %s CASCADE' % row[0])
						print("dropping sequence %s" % row[0])
					except Exception as e:
						print("couldn't drop sequence %s" % row[0])
				print("Postgres Database Schema was reset")
		except Exception as e:
			print(e)