from django.test import TestCase
from django.core import mail

from ovp.apps.core.helpers import get_email_subject, is_email_enabled
from ovp.apps.users.models import User
from ovp.apps.projects.models import Project, Apply


class TestEmailTriggers(TestCase):

    def test_project_creation_trigger_email(self):
        """
        Assert that email is triggered when creating a project
        """
        user = User.objects.create_user(
            email="test_project@project.com",
            password="test_project",
            object_channel="default"
        )
        mail.outbox = []  # Mails sent before creating don't matter
        project = Project.objects.create(
            name="test project",
            slug="test project",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )

        if is_email_enabled("default", "projectCreated"):
            self.assertTrue(len(mail.outbox) == 1)
            self.assertTrue(
                mail.outbox[0].subject
                == get_email_subject(
                    "default", "projectCreated", "Project created"
                )
            )
        else:  # pragma: no cover
            self.assertTrue(len(mail.outbox) == 0)

    def test_project_publishing_trigger_email(self):
        """
        Assert that email is triggered when publishing a project
        """
        user = User.objects.create_user(
            email="test_project@project.com",
            password="test_project",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test project",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )

        mail.outbox = []  # Mails sent before publishing don't matter
        project.published = True
        project.save()

        if is_email_enabled("default", "projectPublished"):  # pragma: no cover
            self.assertTrue(len(mail.outbox) == 1)
            self.assertTrue(
                mail.outbox[0].subject
                == get_email_subject(
                    "default", "projectPublished", "Project published"
                )
            )
        else:  # pragma: no cover
            self.assertTrue(len(mail.outbox) == 0)

    def test_project_closing_trigger_email(self):
        """
        Assert that email is triggered when closing a project
        """
        user = User.objects.create_user(
            email="test_project@project.com",
            password="test_project",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test project",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )

        mail.outbox = []  # Mails sent before closing don't matter
        project.closed = True
        project.save()

        if is_email_enabled("default", "projectClosed"):  # pragma: no cover
            self.assertTrue(len(mail.outbox) == 1)
            self.assertTrue(
                mail.outbox[0].subject
                == get_email_subject(
                    "default", "projectClosed", "Project closed"
                )
            )
        else:  # pragma: no cover
            self.assertTrue(len(mail.outbox) == 0)

    def test_apply_trigger_email(self):
        """
        Assert that applying to project trigger one
        email to volunteer and one to project owner
        """
        user = User.objects.create_user(
            email="test_project@project.com",
            password="test_project",
            object_channel="default"
        )
        volunteer = User.objects.create_user(
            email="test_volunteer@project.com",
            password="test_volunteer",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test project",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )

        mail.outbox = []  # Mails sent before applying don't matter
        apply = Apply(project=project, user=volunteer, email=volunteer.email)
        apply.save(object_channel="default")

        recipients = [x.to[0] for x in mail.outbox]
        subjects = [x.subject for x in mail.outbox]

        # pragma: no cover
        if is_email_enabled("default", "volunteerApplied-ToVolunteer"):
            self.assertTrue(
                get_email_subject(
                    "default",
                    "volunteerApplied-ToVolunteer",
                    "Applied to project"
                ) in subjects
            )
            self.assertTrue("test_project@project.com" in recipients)

        # pragma: no cover
        if is_email_enabled("default", "volunteerApplied-ToOwner"):
            self.assertTrue(
                get_email_subject(
                    "default",
                    "volunteerApplied-ToOwner",
                    "New volunteer"
                ) in subjects
            )
            self.assertTrue("test_volunteer@project.com" in recipients)

    def test_unapply_trigger_email(self):
        """
        Assert that applying to project trigger one
        email to volunteer and one to project owner
        """
        user = User.objects.create_user(
            email="test_project@project.com",
            password="test_project",
            object_channel="default"
        )
        volunteer = User.objects.create_user(
            email="test_volunteer@project.com",
            password="test_volunteer",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test project",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )

        mail.outbox = []  # Mails sent before applying don't matter
        apply = Apply(project=project, user=volunteer, email=volunteer.email)
        apply.save(object_channel="default")
        apply.status = "unapplied"
        apply.save()

        recipients = [x.to[0] for x in mail.outbox]
        subjects = [x.subject for x in mail.outbox]

        # pragma: no cover
        if is_email_enabled("default", "volunteerUnapplied-ToVolunteer"):
            self.assertTrue(
                get_email_subject(
                    "default",
                    "volunteerUnapplied-ToVolunteer",
                    "Unapplied from project"
                ) in subjects
            )
            self.assertTrue("test_project@project.com" in recipients)

        # pragma: no cover
        if is_email_enabled("default", "volunteerUnapplied-ToOwner"):
            self.assertTrue(
                get_email_subject(
                    "default",
                    "volunteerUnapplied-ToOwner",
                    "Volunteer unapplied from project"
                ) in subjects
            )
            self.assertTrue("test_volunteer@project.com" in recipients)
