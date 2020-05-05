import collections
import logging
from django.core.management.base import BaseCommand
from django.db import connection
from ovp.apps.users.models.profile import get_profile_model
from ovp.apps.users.models import User
from ovp.apps.organizations.models import Organization

QUERIES = [
    "UPDATE core_post SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE projects_apply SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE uploads_uploadedimage SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE uploads_uploadeddocument SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE projects_project SET owner_id = {new_pk} WHERE owner_id = {old_pk} RETURNING id, owner_id;",
    "UPDATE projects_projectbookmark SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE organizations_organization SET owner_id = {new_pk} WHERE owner_id = {old_pk} RETURNING id, owner_id;",
    "UPDATE organizations_organizationbookmark SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE gallery_gallery SET owner_id = {new_pk} WHERE owner_id = {old_pk} RETURNING id, owner_id;",
    "UPDATE donations_subscription SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE donations_transaction SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE users_emailverificationtoken SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE organizations_organization_members SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE users_passwordhistory SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE users_passwordrecoverytoken SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE social_auth_usersocialauth SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE ratings_rating SET owner_id = {new_pk} WHERE owner_id = {old_pk} RETURNING id, owner_id;",
    "UPDATE ratings_ratingrequest SET requested_user_id = {new_pk} WHERE requested_user_id = {old_pk} RETURNING id, requested_user_id;",
    "UPDATE ratings_ratingrequest SET initiator_id = {new_pk} WHERE initiator_id = {old_pk} AND initiator_type_id = (SELECT id FROM django_content_type WHERE model='project') RETURNING id, initiator_id;",
    "UPDATE organizations_organizationinvite SET invited_id = {new_pk} WHERE invited_id = {old_pk} RETURNING id, invited_id;",
    "UPDATE organizations_organizationinvite SET invitator_id = {new_pk} WHERE invitator_id = {old_pk} RETURNING id, invitator_id;",

    "UPDATE oauth2_provider_application SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE oauth2_provider_grant SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE oauth2_provider_accesstoken SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
    "UPDATE oauth2_provider_refreshtoken SET user_id = {new_pk} WHERE user_id = {old_pk} RETURNING id, user_id;",
]

def move_profile(old, new, dry_run=True):
    if not old.profile:
        get_profile_model().objects.create(user=old, object_channel=old.channel.slug)

    if not new.profile:
        get_profile_model().objects.create(user=new, object_channel=new.channel.slug)

    # Merge profile fields
    fields = ['full_name', 'gender', 'birthday_date', 'about', 'has_done_volunteer_work_before']
    for field in fields:
        old_field = getattr(old.profile, field, None)
        new_field = getattr(new.profile, field, None)
        if not new_field and old_field:
            if not dry_run:
                setattr(new, field, old_field)
            logging.debug(f"Migrating profile field {field}. Old was None, new value is {old_field}")

    # Merge skills and causes
    m2m = ['causes', 'skills']
    for rel in m2m:
        old_rel = getattr(old.profile, rel).all()
        new_rel = getattr(new.profile, rel).all()

        for item in old_rel:
            if item not in new_rel:
                if not dry_run:
                    getattr(new.profile, rel).add(item)
                logging.debug(f"Migrating {rel}: {item.name}")

def move(old_pk, new_pk, dry_run=True):
    """ Move an user data to another """
    logging.info("Moving {} to {}".format(old_pk, new_pk))

    psqlconnection = connection.cursor().connection
    psqlconnection.set_isolation_level(3)
    cursor = psqlconnection.cursor()

    # Migrate relationships except
    # for LogEntry and UserProfile objects
    for query in QUERIES:
        prepared = query.format(old_pk=old_pk, new_pk=new_pk)

        logging.debug("Execute: {}".format(prepared))
        cursor.execute(prepared)

        row_count = cursor.fetchall()
        logging.debug("Modifying: {} rows".format(cursor.rowcount))
        if dry_run:
            psqlconnection.rollback()
        else:
            psqlconnection.commit()
    psqlconnection.set_isolation_level(0)

    # Move profile
    old = User.objects.get(pk=old_pk)
    new = User.objects.get(pk=new_pk)
    move_profile(old, new, dry_run)

    # Deactivate user
    email = f"pk-{old.pk}-to-{new.pk}@moved.by.deduplication"
    is_active = False
    if not dry_run:
        User.objects.filter(pk=old_pk).update(email=email, is_active=False)

    old = User.objects.get(pk=old_pk)
    logging.info(f"New email: {old.email}. Activated: {old.is_active}")

def dedup(email, channel, dry_run=True):
    """
    Deduplicate an user, this function will also deal with 3 or more users with the same email.
    """
    users = User.objects.filter(channel__slug=channel, email__iexact=email).order_by('pk')
    main_user = None
    logging.info(email)

    for user in users:
        main_user = user if not main_user else main_user
        apls = user.apply_set.all().count()
        owner_of = Organization.objects.filter(owner=user).count()
        member_of = Organization.objects.filter(members=user).count()
        logging.info("[{}] | PK: {} | Applies: {} | Member of: {} | Owner of: {} | {}".format(
            "X" if main_user == user else " ",
            user.pk,
            apls,
            member_of,
            owner_of,
            user.last_login)
        )

        if user != main_user:
            move(user.pk, main_user.pk, dry_run=dry_run)
    logging.info("---------")

def dedup_all(channel="default", dry_run=True):
    """ Deduplicate all users on a channel which have
    the same email in different cases.
    """
    email_list = list(User.objects.filter(channel__slug=channel).values_list('email', flat=True))
    normalized = [x.lower() for x in email_list]
    duplicates = [item for item, count in collections.Counter(normalized).items() if count > 1]
    for email in duplicates:
        dedup(email, channel, dry_run=dry_run)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'channel',
            help='Channel slug',
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

        dedup_all(options['channel'], not options['run'])
