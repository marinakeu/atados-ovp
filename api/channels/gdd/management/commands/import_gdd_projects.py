from django.core.management.base import BaseCommand
from collections import OrderedDict
from ovp.apps.users.models import User
from ovp.apps.users.models import UserProfile
from ovp.apps.projects.models import Project
from ovp.apps.projects.models import VolunteerRole
from ovp.apps.core.models import GoogleAddress
from ovp.apps.organizations.models import Organization
from ovp.apps.core.models import Cause
from ovp.apps.projects.models import Job, JobDate
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import pytz
import random
import string
import logging
import csv
import copy

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        self.pwdict = {}
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            help='CSV file',
            type=str,
        )

        parser.add_argument(
            '--run',
            help='Do an actual run instead of dry run',
            action='store_true',
        )

    def handle(self, *args, **options):
        # Converts value from verbosity int to logging library
        # level.
        # 1 -> 30 (logging.WARNING)
        # 2 -> 20 (logging.INFO)
        # 3 -> 10 (logging.DEBUG)
        loggingLevel = 40 - (options['verbosity'] * 10)

        logger = logging.getLogger()
        console = logging.StreamHandler()

        logger.setLevel(loggingLevel)
        console.setLevel(loggingLevel)

        logger.addHandler(console)
        self.dry_run = not options['run']
        self._process_csv(options['file'])

    def _process_csv(self, file_path: str) -> None:
        with open(file_path) as csv_file:
            spamreader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
            for row in spamreader:
                self._process_row(row)

    def _process_row(self, row: OrderedDict):
        logging.debug('Processing project {}'.format(row['Project: Project Name']))

        # User data
        user_data: dict = {
            'email': row['C Email'],
            'name': f"{row['C First Name']} {row['C last Name']}",
            'phone': row['C_phone']
        }
        user: User = self._get_or_create_user(user_data)

        # Organization address data
        address_data: dict = {
            'typed_address': f"{row['O Street']}, {row['District ']}, {row['O city']}, {row['O_country']}'",
            'typed_address2': row['Add-on']
        }
        address: GoogleAddress = self._create_address(address_data)

        # Organization data
        organization_data: dict = {
            'owner_id': user.pk,
            'address_id': address.pk,
            'name': row['Organization: Organization Name'],
            'contact_name': f"{row['C First Name']} {row['C last Name']}",
            'contact_email': row['C Email'],
            'contact_phone': row['C_phone'],
        }
        organization: Organization = self._get_or_create_organization(organization_data)

        # Organization address data
        address: GoogleAddress = self._create_address(address_data)

        # Project data
        project_data: dict = {
            'owner_id': user.pk,
            'address_id': address.pk,
            'organization_id': organization.pk,
            'name': row['Project: Project Name'],
            'description': row['Project Description'],
            'max_applies': row['Number of Participants Final'],
            'published': True
        }
        role_data = self._get_role_data(row['Language'], row['Number of Participants Final'])
        causes = self._get_causes(row['Type'].split(';'))
        job = self._get_job(row['Date of GDD project(s)'])
        self._create_project(project_data, role_data, causes, job)


        print('-------')

    def _get_or_create_user(self, data: dict) -> User:
        email = data['email']
        try:
            logging.debug(f'Getting user {email}')
            user = User.objects.get(email=email, channel__slug="gdd")
        except User.DoesNotExist:
            logging.debug(f'Failed. Creating user {email}')

            password = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(12)])
            self.pwdict[email] = password

            user = User(**data)

            if not self.dry_run:
                user.save(object_channel="gdd")

            profile = UserProfile(user = user)
            if not self.dry_run:
                profile.save(object_channel="gdd")

        return user

    def _get_or_create_organization(self, data: dict) -> Organization:
        name = data['name']
        try:
            logging.debug(f'Getting organization {name}')
            organization = Organization.objects.get(name=name, channel__slug="gdd")
        except Organization.DoesNotExist:
            logging.debug(f'Failed. Creating organization {name}')

            organization = Organization(**data)

            if not self.dry_run:
                organization.save(object_channel="gdd")

        return organization

    def _create_address(self, address_data: dict) -> GoogleAddress:
        logging.debug(f'Creating address {address_data["typed_address"]}')
        address = GoogleAddress(**address_data)
        if not self.dry_run:
            address.save(object_channel="gdd")
        return address

    def _create_project(self, project_data: dict, role_data: dict, causes: list, job: Job) -> Project:
        logging.debug(f'Creating project {project_data["name"]}')
        project = Project(**project_data)
        if not self.dry_run:
            project.save(object_channel="gdd")
            role_data['project_id'] = project.pk

        role = VolunteerRole(**role_data)
        if not self.dry_run:
            role.save(object_channel="gdd")

            for cause in causes:
                project.causes.add(cause)

            job.project = project
            job.save()


        return project

    def _get_causes(self, causes_field: str) -> list:
        cause_mapping = {
            'Environment': 'Environment',
            'Elderly care': 'Elders',
            'Education': 'Education',
            'Special populations': 'Citizen Participation',
            'Animals': 'Animal Protection',
            'Other': None
        }
        causes_names = [x.strip() for x in causes_field]
        causes = []
        for cause in causes_names:
            print(cause)
            name = cause_mapping[cause]
            if name:
                causes.append(
                    Cause.objects.get(name=name, channel__slug='gdd')
                )
        return causes

    def _get_role_data(self, language, vacancies):
        languages = {
            'en-us': {
                'name': 'Volunteer',
                'prerequisites': 'Have full day disponibility on Good Deeds Day',
            },
            'es-ar': {
                'name': 'Voluntario',
                'prerequisites': 'Tener disponibilidad de día completo en el día de buenas acciones',
            },
            'pt-br': {
                'name': 'Voluntário',
                'prerequisites': 'Tener disponibilidad de día completo en el día de buenas acciones',
            }
        }

        role_data = copy.deepcopy(languages[language])
        role_data['vacancies'] = vacancies
        return role_data

    def _get_job(self, date):
        job = Job()

        if not self.dry_run:
            job.save(object_channel="gdd")

        tz = pytz.timezone('America/Argentina/Buenos_Aires' )
        start_date = tz.localize(parse(date))
        end_date = start_date + relativedelta(hours=24)
        jobdate = JobDate(start_date=start_date, end_date=end_date, job=job)

        if not self.dry_run:
            jobdate.save(object_channel="gdd")

        return job
