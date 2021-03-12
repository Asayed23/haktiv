from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests
import random
from main.users.models import User, RegisteredUser
from main.core.models import Currency, EmailServer
from main.programs.models import *
from main.users.models import *
from main.filemanager.models import *
from django.contrib.auth.hashers import make_password, check_password
import datetime
from dateutil.parser import parse
from django.core.files import File
import os
user_attrs = dict(
    is_active=True,
    is_staff=False,
    is_superuser=False,
    is_email=True,
    is_verified=True,
)


bugs_list = ["Allocation of Resources Without Limits or Throttling CWE-770",
"Array Index Underflow CWE-129",
"Authentication Bypass Using an Alternate Path or Channel CWE-288",
"Brute Force CWE-307",
"Buffer Over-read CWE-126",
"Buffer Underflow CWE-124",
"Buffer Under-read CWE-127",
"Business Logic Errors CWE-840",
"Classic Buffer Overflow CWE-120",
"Cleartext Storage of Sensitive Information CWE-312",
"Cleartext Transmission of Sensitive Information CWE-319",
"Client-Side Enforcement of Server-Side Security CWE-602",
"Code Injection CWE-94",
"Command Injection - Generic CWE-77",
"Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition') CWE-362",
"CRLF Injection CWE-93",
"Cross-Site Request Forgery (CSRF) CWE-352",
"Cross-site Scripting (XSS) - DOM CWE-79",
"Cross-site Scripting (XSS) - Generic CWE-79",
"Cross-site Scripting (XSS) - Reflected CWE-79",
"Cross-site Scripting (XSS) - Stored CWE-79",
"Cryptographic Issues - Generic CWE-310",
"Denial of Service CWE-400",
"Deserialization of Untrusted Data CWE-502",
"Double Free CWE-415",
"Download of Code Without Integrity Check CWE-494",
"Embedded Malicious Code CWE-506",
"Execution with Unnecessary Privileges CWE-250",
"Exposed Dangerous Method or Function CWE-749",
"External Control of Critical State Data CWE-642",
"Externally Controlled Reference to a Resource in Another Sphere CWE-610",
"Failure to Sanitize Special Elements into a Different Plane (Special Element Injection) CWE-75",
"File and Directory Information Exposure CWE-538",
"Forced Browsing CWE-425",
"Heap Overflow CWE-122",
"HTTP Request Smuggling CWE-444",
"HTTP Response Splitting CWE-113",
"Improper Access Control - Generic CWE-284",
"Improper Authentication - Generic CWE-287",
"Improper Authorization CWE-285",
"Improper Certificate Validation CWE-295",
"Improper Check or Handling of Exceptional Conditions CWE-703",
"Improper Export of Android Application Components CWE-926",
"Improper Following of a Certificate's Chain of Trust CWE-296",
"Improper Handling of Highly Compressed Data (Data Amplification) CWE-409",
"Improper Handling of Insufficient Permissions or Privileges CWE-280",
"Improper Handling of URL Encoding (Hex Encoding) CWE-177",
"Improper Input Validation CWE-20",
"Improper Neutralization of Escape, Meta, or Control Sequences CWE-150",
"Improper Neutralization of HTTP Headers for Scripting Syntax CWE-644",
"Improper Neutralization of Script-Related HTML Tags in a Web Page (Basic XSS) CWE-80",
"Improper None Termination CWE-170",
"Improper Privilege Management CWE-269",
"Inadequate Encryption Strength CWE-326",
"Inclusion of Functionality from Untrusted Control Sphere CWE-829",
"Incomplete Blacklist CWE-184",
"Incorrect Authorization CWE-863",
"Incorrect Calculation of Buffer Size CWE-131",
"Incorrect Comparison CWE-697",
"Incorrect Permission Assignment for Critical Resource CWE-732",
"Information Disclosure CWE-200",
"Information Exposure Through an Error Message CWE-209",
"Information Exposure Through Debug Information CWE-215",
"Information Exposure Through Directory Listing CWE-548",
"Information Exposure Through Discrepancy CWE-203",
"Information Exposure Through Sent Data CWE-201",
"Information Exposure Through Timing Discrepancy CWE-208",
"Insecure Direct Object Reference (IDOR) CWE-639",
"Insecure Storage of Sensitive Information CWE-922",
"Insecure Temporary File CWE-377",
"Insufficiently Protected Credentials CWE-522",
"Insufficient Session Expiration CWE-613",
"Integer Overflow CWE-190",
"Integer Underflow CWE-191",
"Key Exchange without Entity Authentication CWE-322",
"LDAP Injection CWE-90",
"Leftover Debug Code (Backdoor) CWE-489",
"Malware CAPEC-549",
"Man-in-the-Middle CWE-300",
"Memory Corruption - Generic CWE-119",
"Misconfiguration CWE-16",
"Missing Authentication for Critical Function CWE-306",
"Missing Authorization CWE-862",
"Missing Encryption of Sensitive Data CWE-311",
"Missing Required Cryptographic Step CWE-325",
"Modification of Assumed-Immutable Data (MAID) CWE-471",
"None Pointer Dereference CWE-476",
"Off-by-one Error CWE-193",
"Open Redirect CWE-601",
"OS Command Injection CWE-78",
"Out-of-bounds Read CWE-125",
"Password in Configuration File CWE-260",
"Path Traversal CWE-22",
"Path Traversal: '.../...//' CWE-35",
"Phishing CAPEC-98",
"Plaintext Storage of a Password CWE-256",
"Privacy Violation CWE-359",
"Privilege Escalation CAPEC-233",
"Relative Path Traversal CWE-23",
"Reliance on Cookies without Validation and Integrity Checking in a Security Decision CWE-784",
"Reliance on Reverse DNS Resolution for a Security-Critical Action CWE-350",
"Reliance on Untrusted Inputs in a Security Decision CWE-807",
"Remote File Inclusion CWE-98",
"Replicating Malicious Code (Virus or Worm) CWE-509",
"Resource Injection CWE-99",
"Reusing a Nonce, Key Pair in Encryption CWE-323",
"Reversible One-Way Hash CWE-328",
"Security Through Obscurity CWE-656",
"Server-Side Request Forgery (SSRF) CWE-918",
"Session Fixation CWE-384",
"SQL Injection CWE-89",
"Stack Overflow CWE-121",
"Storing Passwords in a Recoverable Format CWE-257",
"Time-of-check Time-of-use (TOCTOU) Race Condition CWE-367",
"Trust of System Event Data CWE-360",
"Type Confusion CWE-843",
"UI Redressing (Clickjacking) CAPEC-103",
"Unchecked Error Condition CWE-391",
"Uncontrolled Recursion CWE-674",
"Unprotected Transport of Credentials CWE-523",
"Unrestricted Upload of File with Dangerous Type CWE-434",
"Untrusted Search Path CWE-426",
"Unverified Password Change CWE-620",
"Use After Free CWE-416",
"Use of a Broken or Risky Cryptographic Algorithm CWE-327",
"Use of a Key Past its Expiration Date CWE-324",
"Use of Cryptographically Weak Pseudo-Random Number Generator (PRNG) CWE-338",
"Use of Externally-Controlled Format String CWE-134",
"Use of Hard-coded Credentials CWE-798",
"Use of Hard-coded Cryptographic Key CWE-321",
"Use of Hard-coded Password CWE-259",
"Use of Inherently Dangerous Function CWE-242",
"Use of Insufficiently Random Values CWE-330",
"User Interface (UI) Misrepresentation of Critical Information CWE-451",
"Violation of Secure Design Principles CWE-657",
"Weak Cryptography for Passwords CWE-261",
"Weak Password Recovery Mechanism for Forgotten Password CWE-640",
"Wrap-around Error CWE-128",
"Write-what-where Condition CWE-123",
"XML Entity Expansion CWE-776",
"XML External Entities (XXE) CWE-611",
"XML Injection CWE-91",
"XSS Using MIME Type Mismatch CAPEC-209"]



burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0", "Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://hackerone.com/reports/6504", "X-CSRF-Token": "DWfULGbOSr14+KO0gRpTUzKLm/oNyXLOMtlMfQZ4MTUjbKloyKhtlUdbXyL8YsA9ws9x94R+Oya+Oc9DiUlbdg==", "X-Requested-With": "XMLHttpRequest", "Connection": "close"}

def get_program_data(handle):
    burp0_url = f"https://hackerone.com:443/{handle}"
    try:
        s= requests.get(burp0_url, headers=burp0_headers)
        if s.status_code == 200:
            return s.json()
    except Exception as e:
        print(e)
        pass
    return False
    




def load_programs():
    burp0_url = "https://hackerone.com:443/graphql"
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://hackerone.com/directory/programs?order_direction=DESC&order_field=resolved_report_count", "content-type": "application/json", "X-Auth-Token": "----", "Origin": "https://hackerone.com", "Connection": "close"}
    burp0_json={"operationName":"DirectoryQuery","variables":{"where":{"_and":[{"_or":[{"submission_state":{"_eq":"open"}},{"submission_state":{"_eq":"api_only"}},{"external_program":{}}]},{"_not":{"external_program":{}}},{"_or":[{"_and":[{"state":{"_neq":"sandboxed"}},{"state":{"_neq":"soft_launched"}}]},{"external_program":{}}]}]},"first":50,"secureOrderBy":{"reports":{"resolved_count":{"_direction":"DESC"}}}},"query":"query DirectoryQuery($cursor: String, $secureOrderBy: FiltersTeamFilterOrder, $where: FiltersTeamFilterInput) {\n  me {\n    id\n    edit_unclaimed_profiles\n    h1_pentester\n    __typename\n  }\n  teams(first: 25, after: $cursor, secure_order_by: $secureOrderBy, where: $where) {\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    edges {\n      node {\n        id\n        bookmarked\n        ...TeamTableResolvedReports\n        ...TeamTableAvatarAndTitle\n        ...TeamTableLaunchDate\n        ...TeamTableMinimumBounty\n        ...TeamTableAverageBounty\n        ...BookmarkTeam\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TeamTableResolvedReports on Team {\n  id\n  resolved_report_count\n  __typename\n}\n\nfragment TeamTableAvatarAndTitle on Team {\n  id\n  profile_picture(size: medium)\n  name\n  handle\n  submission_state\n  triage_active\n  publicly_visible_retesting\n  state\n  external_program {\n    id\n    __typename\n  }\n  ...TeamLinkWithMiniProfile\n  __typename\n}\n\nfragment TeamLinkWithMiniProfile on Team {\n  id\n  handle\n  name\n  __typename\n}\n\nfragment TeamTableLaunchDate on Team {\n  id\n  started_accepting_at\n  __typename\n}\n\nfragment TeamTableMinimumBounty on Team {\n  id\n  currency\n  base_bounty\n  __typename\n}\n\nfragment TeamTableAverageBounty on Team {\n  id\n  currency\n  average_bounty_lower_amount\n  average_bounty_upper_amount\n  __typename\n}\n\nfragment BookmarkTeam on Team {\n  id\n  bookmarked\n  __typename\n}\n"}
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
        try:
            triager.save()
        except:
            pass
    
    try:

        s = requests.post(burp0_url, headers=burp0_headers, json=burp0_json)
        if s.status_code == 200:
            data = s.json()
            for i in data['data']['teams']['edges']:
                if i['__typename'] == "TeamEdge":
                    program_data = i['node']
                    reward_type = random.choice(Program.REWARD_TYPES)[0]
                    status = random.choice(Program.STATUSES)[0]
                    visibility = random.choice(Program.VISIBILITIES)[0]
                    title = program_data['name']
                    handle = program_data['handle']
                    programd = get_program_data(handle)
                    if programd:
                        try:
                            customer,customercreated = User.objects.get_or_create(
                            first_name=f"{title}",
                            last_name="Manager",
                            email=f"{title}@{title}.com",
                            username=f"{title}@{title}.com",
                            password=make_password(f"manager@{title}.com"),
                            role=User.CUSTOMER,
                            **user_attrs
                            )
                        except Exception as e:
                            customer = User.objects.get(
                                username=f"{title}@{title}.com"
                            )
                        obj = {
                            'title':title,
                            'reward_type':reward_type,
                            'customer':customer,
                            'status':status,
                            'visibility':visibility,
                            'website':f"{handle}.com",
                            'launch_date': parse(program_data['started_accepting_at']).date(),
                        }
                        obj['bio'] = programd['profile']['about']
                        obj['policy'] = programd['policy_markdown']
                        urlpt = str(programd['profile_picture_urls']['xtralarge'])

                        programobject,programobjectcreated = Program.objects.get_or_create(title=title,launch_date=parse(program_data['started_accepting_at']).date())
                        programobject.title = title
                        programobject.reward_type = reward_type
                        programobject.customer = customer
                        programobject.status = status
                        programobject.visibility = visibility
                        programobject.website = f"{handle}.com"
                        programobject.policy = programd['policy_markdown']
                        programobject.bio = programd['profile']['about']
                        programobject.save()
                        dw = Program.objects.filter(id=programobject.id)
                        dw.update(**obj)
                        if urlpt:
                            pass
                            image_stream = requests.get(urlpt, stream=True)
                            open('img.png', 'wb').write(image_stream.content)
                            local_file = open('img.png','rb')
                            djangofile = File(local_file)
                            FileManagerobj,created = FileManager.objects.get_or_create(title=title,source=djangofile)
                            programobject.logo = FileManagerobj
                            programobject.save()
                            local_file.close()
                            os.remove('img.png')
                            print("Downloading image " + str(FileManagerobj))

                        for i in range(random.randint(1,4)):
                            try:
                                triager = random.choice(triagers_list)
                                triagerobj = User.objects.get(username=triager.username)
                                programobject.triagers.add(triagerobj)
                                programobject.save()                                
                            except Exception as e:
                                print(e)
                                pass

                        print('Program Loaded '+title)
    except Exception as e:
        print(e)
        pass
    return False


def load_reports():
    urls = [
        "https://hackerone.com/reports/1005421.json",
        "https://hackerone.com/reports/317321.json",
        "https://hackerone.com/reports/874778.json",
        "https://hackerone.com/reports/974222.json",
        "https://hackerone.com/reports/910300.json",
        "https://hackerone.com/reports/905607.json",
        "https://hackerone.com/reports/295841.json",
    ]

#   "structured_scope": {
#     "databaseId": 3802,
#     "asset_type": "URL",
#     "asset_identifier": "https://www.tube8.fr/",
#     "max_severity": "critical"
#   },


    #dict_keys(['id', 'global_id', 'url', 'title', 'state', 'substate', 'severity_rating', 'readable_substate', 'created_at', 'submitted_at', 'is_member_of_team?', 'reporter', 'team', 'has_bounty?', 'in_validation?', 'rejected_anc_report_that_can_be_sent_back_to_anc_triagers?', 'can_view_team', 'can_view_report', 'is_external_bug', 'is_published', 'is_participant', 'stage', 'public', 'visibility', 'cve_ids', 'singular_disclosure_disabled', 'disclosed_at', 'bug_reporter_agreed_on_going_public_at', 'team_member_agreed_on_going_public_at', 'comments_closed?', 'facebook_team?', 'team_private?', 'vulnerability_information', 'vulnerability_information_html', 'bounty_amount', 'formatted_bounty', 'weakness', 'original_report_id', 'original_report_url', 'attachments', 'allow_singular_disclosure_at', 'allow_singular_disclosure_after', 'singular_disclosure_allowed', 'vote_count', 'voters', 'severity', 'structured_scope', 'abilities', 'can_edit_custom_fields_attributes', 'activities', 'activity_page_count', 'activity_page_number', 'summaries'])
    for url in urls:
        try:
            s= requests.get(url, headers=burp0_headers)
            if s.status_code == 200:
                js = s.json()
                title = js['title']
                document_state = random.choice(ProgramReport.DOCUMENT_STATES)[0]
                asset = js['structured_scope']['asset_identifier'] if js['structured_scope'] else "main"
                visibility = random.choice(ProgramReport.VISIBILITIES)[0]
                status = random.choice(ProgramReport.STATUSES)[0]
                category = random.choice(ProgramReport.CATEGORIES)[0]
                severity = random.choice(ProgramReport.SEVERITIES)[0]
                vulnerabilityname = js['weakness']['name'] if js['weakness'] else "main"
                program = Program.objects.filter().order_by('?').first()
                description = js['vulnerability_information_html']
                impact = ""
                recommendation = impact
                resname = js['reporter']['username']
                try:
                    researcher,researchercreated = User.objects.get_or_create(
                        first_name=f"{js['reporter']['username']}",
                        last_name="researcher",
                        email=f"{resname}@{title}.com",
                        username=f"{resname}@{title}.com",
                        password=make_password(f"resname@{title}.com"),
                        role=User.RESEARCHER,
                        **user_attrs                
                    ) 
                except Exception as e:
                    researcher = User.objects.get(
                        username=f"{resname}@{title}.com"
                    )
                triager = program.triagers.all()[0]
                try:
                    vulnerability,bee = ProgramVulnerability.objects.get_or_create(name=vulnerabilityname)
                    ProgramReportobject = ProgramReport(
                        title=title,
                        triager=triager,
                        researcher=researcher,
                        recommendation=recommendation,
                        impact=impact,
                        description=description,
                        program=program,
                        vulnerability=vulnerability,
                        severity=severity,
                        category=category,
                        status=status,
                        visibility=visibility,
                        asset=asset,
                        document_state=document_state,
                    )
                    ProgramReportobject.save()
                    print(ProgramReportobject)
                except Exception as e:
                    print(e)
                    pass

                
        except Exception as e:
            print(e)
            pass

def load_vulns():
    for bug in bugs_list:
        ProgramVulnerabilityobject, created = ProgramVulnerability.objects.get_or_create(name=bug)
        print("Loaded Vulnerability "+ str(ProgramVulnerabilityobject))


class Command(BaseCommand):
    help = "This command to load hackerone scrapped data into database"
    def handle(self, *args, **options):
        load_programs()
        load_vulns()
