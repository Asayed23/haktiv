import random
import string
import sys
import os
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.core.files import File
from django.conf import settings

from main.core.utils import lorem, password_generator
from main.users.models import User
from main.filemanager.models import FileManager
from .dumy import in_scope_assets, out_scope_assets, top_1000_domains, top_1000_subdomains
from ..models import Program, ProgramTypeTag, ProgramHallOfFame, ProgramReward, ProgramReport, ProgramReportActivity, \
    ProgramVulnerability, ProgramScope

give_random_number = lambda a, b: random.randint(a, b)


def shuffled(x):
    random.shuffle(x)
    return x


def get_sequence_id():
    return f"{password_generator(size=2, chars=string.ascii_uppercase)}{str(random.randint(101, 99999)).zfill(5)}"


def get_random_subdomains(domain):
    subdomain = random.choice(top_1000_subdomains)
    return f"{subdomain}.{domain}"

def get_file_path(filename):
    return str(settings.APPS_DIR.path(f"{filename}"))

def get_file_manager(filename):
    file_manager = FileManager.objects.create()
    file = File(open(get_file_path(f'static/assets/img/logo/{filename}') ,'rb'))
    file_manager.source.save(filename, file, save=True)
    return file_manager

pre_populated_domain_list = []


def load_customers():
    user_attrs = dict(
        is_active=True,
        is_staff=False,
        is_superuser=False,
        is_email=True,
        is_verified=True,
    )
    customers_list = [
        User(
            first_name="Mohammed",
            last_name="Nader",
            email="customer21@example.com",
            username="customer21@example.com",
            password=make_password("customer21@example.com"),
            role=User.CUSTOMER,
            **user_attrs
        ),
        User(
            first_name="Khaled",
            last_name="Soufi",
            email="customer22@example.com",
            username="customer22@example.com",
            password=make_password("customer22@example.com"),
            role=User.CUSTOMER,
            **user_attrs
        ),
        User(
            first_name="Sofia",
            last_name="Serpentine",
            email="customer23@example.com",
            username="customer23@example.com",
            password=make_password("customer23@example.com"),
            role=User.CUSTOMER,
            **user_attrs
        )
    ]
    for customer in customers_list:
        customer.save()


def load_triagers():
    user_attrs = dict(
        is_active=True,
        is_staff=False,
        is_superuser=False,
        is_email=True,
        is_verified=True,
    )
    triagers_list = [
        User(
            first_name="Faisal",
            last_name="Kasimi",
            email="triager40@example.com",
            username="triager40@example.com",
            password=make_password("triager40@example.com"),
            role=User.TRIAGER,
            **user_attrs
        ),
        User(
            first_name="Noura",
            last_name="Kayali",
            email="triager41@example.com",
            username="triager41@example.com",
            password=make_password("triager41@example.com"),
            role=User.TRIAGER,
            **user_attrs
        ),
        User(
            first_name="Tony",
            last_name="Awwad",
            email="triager42@example.com",
            username="triager42@example.com",
            password=make_password("triager42@example.com"),
            role=User.TRIAGER,
            **user_attrs
        )
    ]
    for triager in triagers_list:
        triager.save()


def load_hackers():
    user_attrs = dict(
        is_active=True,
        is_staff=False,
        is_superuser=False,
        is_email=True,
        is_verified=True,
    )
    hackers_list = [
        User(
            first_name="Lola",
            last_name="Popen",
            email="researcher90@example.com",
            username="researcher90@example.com",
            password=make_password("researcher90@example.com"),
            role=User.RESEARCHER,
            **user_attrs
        ),
        User(
            first_name="Nunlo",
            last_name="Rita",
            email="researcher92@example.com",
            username="researcher92@example.com",
            password=make_password("researcher92@example.com"),
            role=User.RESEARCHER,
            **user_attrs
        ),
        User(
            first_name="Fatali",
            last_name="Kano",
            email="researcher93@example.com",
            username="researcher93@example.com",
            password=make_password("researcher93@example.com"),
            role=User.RESEARCHER,
            **user_attrs
        )
    ]
    for hacker in hackers_list:
        hacker.save()


def load_vulns():
    ProgramVulnerability.objects.bulk_create([
        ProgramVulnerability(name="VULNERABLE-001"),
        ProgramVulnerability(name="VULNERABLE-002"),
        ProgramVulnerability(name="VULNERABLE-003"),
        ProgramVulnerability(name="VULNERABLE-004"),
        ProgramVulnerability(name="VULNERABLE-005"),
        ProgramVulnerability(name="VULNERABLE-006"),
        ProgramVulnerability(name="VULNERABLE-007"),
        ProgramVulnerability(name="VULNERABLE-008"),
        ProgramVulnerability(name="Other"),
    ])


def load_programs():
    load_customers()
    load_triagers()
    load_hackers()
    load_vulns()
    ###############
    ############### PROGRAM 1
    ###############
    program_params_list = [
        dict(
            title="Wikipedia Program",
            website="https://wikipedia.com",
            logo=get_file_manager(filename='wikipedia.png'),
        ),
        dict(
            title="Netflix Program",
            website="https://netflix.com",
            logo=get_file_manager(filename='netflix.png'),
        ),
        dict(
            title="Facebook Program",
            website="https://facebook.com",
            logo=get_file_manager(filename='facebook.png'),
        ),
        dict(
            title="HP Program",
            website="https://www.hp.com",
            logo=get_file_manager(filename='hp.png'),
        ),
        dict(
            title="SIEMENS Technology Program",
            website="https://www.siemens.de",
            logo=get_file_manager(filename='siemens.jpg'),
        ),
        dict(
            title="HALA Science Program",
            website="https://www.hala.se",
            logo=get_file_manager(filename='hala.png'),
        ),
        dict(
            title="Volkswagen Program",
            website="https://www.volkswagen.eg",
            logo=get_file_manager(filename='volkswagen.jpg'),
        ),
        dict(
            title="Vodafone Expert Program",
            website="https://www.vodafone.com",
            logo=get_file_manager(filename='vodafone.jpg'),
        ),
        dict(
            title="DW Channels Program",
            website="https://www.dw.de",
            logo=get_file_manager(filename='dw.jpg'),
        ),
        dict(
            title="Western Digital Program",
            website="https://www.wd.co.uk",
            logo=get_file_manager(filename='western-digital.jpg'),
        )
    ]
    program_reward_params_list = [
        [
            dict(swag="T-Shirt", points=1000, bounty=100.0, ),
            dict(swag="PlayStation 4", points=3000, bounty=300.0, ),
            dict(swag="LCD TV", points=5000, bounty=500.0, )
        ],
        [
            dict(swag="MAC Book Pro", points=5300, bounty=0.0, ),
            dict(swag="iPhone 6", points=1300, bounty=0.0, ),
        ],
        [
            dict(swag="10k points", points=10000, bounty=0.0, ),
            dict(swag="5k points", points=5000, bounty=0.0, ),
        ],
        [
            dict(swag="HP Printer + LCD HP", points=3000, bounty=0.0, ),
            dict(swag="HP LABTOP", points=7000, bounty=0.0, ),
        ],
        [
            dict(swag="", points=10000, bounty=0.0, ),
            dict(swag="", points=20000, bounty=0.0, ),
            dict(swag="", points=30000, bounty=0.0, ),
            dict(swag="", points=40000, bounty=0.0, ),
        ],
        [
            dict(swag="", points=1000, bounty=0.0, ),
            dict(swag="", points=2000, bounty=0.0, ),
        ],
        [
            dict(swag="", points=10000, bounty=1000.0, ),
            dict(swag="", points=20000, bounty=3000.0, ),
        ],
        [
            dict(swag="", points=10000, bounty=1000.0, ),
            dict(swag="", points=20000, bounty=3000.0, ),
        ],
        [
            dict(swag="T-Shirt", points=2000, bounty=0.0, ),
            dict(swag="Stickers", points=4000, bounty=0.0, ),
            dict(swag="Sky Board", points=5000, bounty=0.0, ),
        ],
        [
            dict(swag="", points=10000, bounty=0.0, ),
            dict(swag="", points=40000, bounty=0.0, ),
            dict(swag="", points=80000, bounty=0.0, ),
        ],
    ]
    for index, program_params in enumerate(program_params_list):
        program = Program.objects.create(
            status=random.choice([key for key, val in Program.STATUSES]),
            visibility=random.choice([key for key, val in Program.VISIBILITIES]),
            reward_type=random.choice([key for key, val in Program.REWARD_TYPES]),
            customer=User.objects.filter(role=User.CUSTOMER).order_by("?").first(),
            bio=lorem.text(),
            scope_description=lorem.text(),
            policy=lorem.paragraph() * random.randint(1, 5),
            launch_date=lorem.random_date(),
            **program_params,
        )
        program.tags.set(
            ProgramTypeTag.objects.filter(name__in=shuffled([x for x, y in ProgramTypeTag.PROGRAM_TYPE_TAGS])).order_by(
                "?"))
        program.triagers.set(User.objects.filter(role=User.TRIAGER).order_by("?")[:give_random_number(1, 3)])
        program.hackers.set(User.objects.filter(role=User.RESEARCHER).order_by("?")[:give_random_number(1, 3)])
        program.save()
        ProgramReward.objects.bulk_create([
            ProgramReward(program=program, **program_reward_params)
            for program_reward_params in program_reward_params_list[index]
        ])
        program_scopes = []
        for key in range(0, random.randint(5, 25)):
            program_scopes.append(ProgramScope(
                program=program,
                scope_type=random.choice([key for key, val in ProgramScope.SCOPE_TYPES]),
                scope_status=random.choice([key for key, val in ProgramScope.SCOPE_STATUSES]),
                # is_eligible=random.choice([True, False]),
                in_scope_asset=lorem.sentence(),
            ))
        ProgramScope.objects.bulk_create(program_scopes)
        hof_params_list = []
        for hacker in program.hackers.order_by("?"):
            hof_params_list.append(ProgramHallOfFame(
                is_top=random.choice([True, False]),
                program=program,
                hacker=hacker,
            ))
        ProgramHallOfFame.objects.bulk_create(hof_params_list)
        # [OBJ] * 3 --> [OBJ, OBJ, OBJ]
        ###############
        ############### PROGRAM REPORTS WITH PROGRAM
        ###############
        program_reports_list = []
        for x in range(1, random.randint(15, 25)):
            domain = random.choice(top_1000_domains)
            researcher = program.hackers.order_by("?").first()
            triager = program.triagers.order_by("?").first()
            report = ProgramReport(
                sequence_id=get_sequence_id(),
                title=lorem.sentence(),
                asset=f"{domain}/*",
                document_state=random.choice([x for x, y in ProgramReport.DOCUMENT_STATES]),
                visibility=random.choice([x for x, y in ProgramReport.VISIBILITIES]),
                status=random.choice([x for x, y in ProgramReport.STATUSES]),
                category=random.choice([x for x, y in ProgramReport.CATEGORIES]),
                severity=random.choice([x for x, y in ProgramReport.SEVERITIES]),
                vulnerability=ProgramVulnerability.objects.order_by("?").first(),
                program=program,
                description=lorem.paragraph(),
                impact=lorem.paragraph(),
                recommendation=lorem.paragraph(),
                researcher=researcher,
                triager=triager,
                urls=[get_random_subdomains(domain=domain) for key in range(0, random.randint(1, 7))]
            )
            program_reports_list.append(report)
        ProgramReport.objects.bulk_create(program_reports_list)
        print(f"Program Report #{index}", len(program_reports_list))
    for index, report in enumerate(ProgramReport.objects.all()):
        for program_scope in ProgramScope.objects.filter(
                scope_status=ProgramScope.IN_SCOPE,
                program=report.program).order_by("?")[:random.randint(1, 3)]:
            report.program_scopes.add(program_scope)
            report.save()
        if report.category != ProgramReport.REJECTED and report.document_state == ProgramReport.PUBLISHED:
            pushed_report = report
            pushed_report.pk = None
            pushed_report.guid = uuid4()
            pushed_report.save()
            report.pushed_reports = pushed_report
            report.save()
        sys.stdout.write(f"\rReport additional data: {index+1}")
        sys.stdout.flush()
    print("\n")
    print("All Program Report added ... [program_scopes], [pushed reports]")

    program_report_activities_list = []
    for key in range(0, random.randint(1000, 5000)):
        program_report_activities_list.append(ProgramReportActivity(
            activity_type=random.choice([x for x, y in ProgramReportActivity.ACTIVITY_TYPES]),
            report=ProgramReport.objects.order_by("?").first(),
            status=random.choice([x for x, y in ProgramReportActivity.STATUSES]),
            comment=lorem.sentence(),
            is_closed=random.choice([True, False]),
            user=User.objects.filter(role__in=[User.RESEARCHER, User.TRIAGER, User.CUSTOMER]).order_by("?").first(),
        ))
        sys.stdout.write(f"\rProgram Report Activity creating: {key+1}")
        sys.stdout.flush()
    ProgramReportActivity.objects.bulk_create(program_report_activities_list)
    print("\n")
    print("Done.")
