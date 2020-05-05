from django.test import TestCase
from django.utils import timezone

from ovp.apps.projects.models import Project
from ovp.apps.projects.models import VolunteerRole
from ovp.apps.projects.models import Work
from ovp.apps.projects.models import Job
from ovp.apps.projects.models import JobDate
from ovp.apps.users.models import User


class ProjectModelTestCase(TestCase):
    def test_project_return_owner_email_and_phone(self):
        """
        Assert the methods .get_phone() and .get_email()
        return owner phone and email address
        """
        phone = "123456789"
        email = "test_returned@test.com"

        user = User.objects.create_user(
            email=email,
            password="test_returned",
            object_channel="default"
        )
        user.phone = phone
        user.save()

        project = Project.objects.create(
            name="test project",
            slug="test slug",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )

        self.assertTrue(project.get_phone() == phone)
        self.assertTrue(project.get_email() == email)

    def test_project_publish(self):
        """ Assert publishing a project updates .published_date """
        user = User.objects.create_user(
            email="test_published@date.com",
            password="test_published_date",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test published date",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )
        self.assertTrue(project.published_date is None)

        project.published = True
        project.save()

        self.assertTrue(project.published_date)

    def test_project_close(self):
        """ Assert closing a project updates .closed_date """
        user = User.objects.create_user(
            email="test_close@date.com",
            password="test_close_date",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test close date",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )
        self.assertTrue(project.closed_date is None)

        project.closed = True
        project.save()

        self.assertTrue(project.closed_date)

    def test_excerpt_from_details(self):
        """
        Assert that if a project has no .description,
        it will use 100 chars from .details as an excerpt
        """
        details = ("a" * 100) + "b"
        expected_description = "a" * 100

        user = User.objects.create_user(
            email="test_excerpt@text.com",
            password="test_excerpt_text",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test excerpt text",
            details=details,
            owner=user,
            object_channel="default"
        )

        project = Project.objects.get(pk=project.id)
        self.assertTrue(project.description == expected_description)

    def test_str_method_returns_name(self):
        """ Assert that .__str__() method returns project name """
        user = User.objects.create_user(
            email="test_str@test.com",
            password="test_str_test",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test str",
            slug="test str test",
            details="abc",
            owner=user,
            object_channel="default"
        )

        self.assertTrue(project.__str__() == "test str")

    def test_slug_generation_on_create(self):
        """ Assert that slug is generated on create """
        user = User.objects.create_user(
            email="test_str@test.com",
            password="test_str_test",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test slug",
            slug="another-slug",
            details="abc",
            owner=user,
            object_channel="default"
        )

        self.assertTrue(project.slug == "test-slug")

    def test_slug_doesnt_repeat(self):
        """ Assert that slug does not repeat """
        user = User.objects.create_user(
            email="test_str@test.com",
            password="test_str_test",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test slug",
            details="abc",
            owner=user,
            object_channel="default"
        )
        self.assertTrue(project.slug == "test-slug")

        project = Project.objects.create(
            name="test slug",
            details="abc",
            owner=user,
            object_channel="default"
        )
        self.assertTrue(project.slug == "test-slug-1")


class VolunteerRoleModelTestCase(TestCase):

    def test_str_method_returns_role_info(self):
        """
        Assert that VolunteerRole.__str__() method returns role info
        """
        role = VolunteerRole(
            name="test role",
            details="a",
            prerequisites="b",
            vacancies=5
        )
        role.save(object_channel="default")

        self.assertTrue(role.__str__() == "test role - a - b (5 vacancies)")

    def test_modifying_roles_update_project_max_applies(self):
        """
        Assert that modifying a role updates Project.max_applies_from_roles
        """
        user = User.objects.create_user(
            email="test_slug@test.com",
            password="test_slug_test",
            object_channel="default"
        )
        project = Project.objects.create(
            details="abc",
            owner=user,
            object_channel="default"
        )
        role = VolunteerRole(
            name="test role",
            details="a",
            prerequisites="b",
            vacancies=5,
            project=project
        )

        self.assertTrue(Project.objects.last().max_applies_from_roles == 0)
        role.save(object_channel="default")
        self.assertTrue(Project.objects.last().max_applies_from_roles == 5)
        role.delete()
        self.assertTrue(Project.objects.last().max_applies_from_roles == 0)


class WorkModelTestCase(TestCase):

    def test_str_method_returns_work_info(self):
        """
        Assert that Work.__str__() method returns hours per week
        """
        work = Work.objects.create(
            weekly_hours=4,
            description="abc",
            object_channel="default"
        )

        self.assertTrue(work.__str__() == "4 hours per week")


class JobModelTestCase(TestCase):

    def test_str_method_returns_job_info(self):
        """
        Assert that Job.__str__() method returns .start_date and .end_date
        """
        user = User.objects.create_user(
            email="test@email.com",
            password="test_email",
            object_channel="default"
        )
        project = Project.objects.create(
            name="test project",
            slug="test slug",
            details="abc",
            description="abc",
            owner=user,
            object_channel="default"
        )

        start = timezone.now()
        end = timezone.now()
        job = Job.objects.create(
            start_date=start,
            end_date=end,
            project=project,
            object_channel="default"
        )

        def human_time(x): return x.strftime("%d/%m/%Y")

        self.assertTrue(
            job.__str__()
            == "{}: {} ~ {}".format(
                project.name, human_time(start), human_time(end)
            )
        )


class JobDateModelTestCase(TestCase):

    def test_str_method_returns_date_info(self):
        """
        Assert that JobDate.__str__() method returns .start_date and .end_date
        """
        start = timezone.now()
        end = timezone.now()

        job = Job()
        job.save(object_channel="default")
        date = JobDate(name="test", start_date=start, end_date=end, job=job)
        date.save(object_channel="default")

        def human_time(x): return x.strftime("%d/%m/%Y %T")

        self.assertTrue(
            date.__str__()
            == "{}: {} ~ {}".format(
                date.name, human_time(start), human_time(end)
            )
        )
