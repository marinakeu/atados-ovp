from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.utils import timezone

from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.utils.serializer_helpers import ReturnList

from ovp.apps.users.models import User

from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Job
from ovp.apps.projects.models import JobDate
from ovp.apps.projects.models import Category
from ovp.apps.projects.serializers.project import ProjectSearchSerializer

from ovp.apps.catalogue.cache import get_catalogue
from ovp.apps.catalogue.cache import fetch_catalogue
from ovp.apps.catalogue.models import Catalogue
from ovp.apps.catalogue.models import Section
from ovp.apps.catalogue.models import SectionFilter


def setUp():
    # Categories
    category1 = Category.objects.create(name="Hot", object_channel="default")
    category2 = Category.objects.create(
        name="Get your hands dirty",
        object_channel="default"
    )
    category3 = Category.objects.create(
        name="Coming up",
        object_channel="default"
    )

    # Catalogue
    catalogue = Catalogue.objects.create(
        name="Home",
        slug="home",
        object_channel="default"
    )

    # Sections
    section1 = Section.objects.create(
        name="Hot",
        slug="hot",
        catalogue=catalogue,
        object_channel="default"
    )
    section1_filter = SectionFilter.objects.create(
        section=section1,
        type="CATEGORY",
        object_channel="default"
    )
    section1_filter.filter.categories.add(category1)

    section2 = Section.objects.create(
        name="Get your hands dirty",
        slug="get-your-hands-dirty",
        catalogue=catalogue,
        object_channel="default"
    )
    section2_filter = SectionFilter.objects.create(
        section=section2,
        type="CATEGORY",
        object_channel="default"
    )
    section2_filter.filter.categories.add(category2)

    section3 = Section.objects.create(
        name="Coming up",
        slug="coming-up",
        catalogue=catalogue,
        object_channel="default"
    )
    section3_filter1 = SectionFilter.objects.create(
        section=section3,
        type="DATEDELTA",
        object_channel="default"
    )
    section3_filter1.filter.operator = "gte"
    section3_filter1.filter.save()

    section3_filter2 = SectionFilter.objects.create(
        section=section3,
        type="DATEDELTA",
        object_channel="default"
    )
    section3_filter2.filter.operator = "lte"
    section3_filter2.filter.weeks = 1
    section3_filter2.filter.save()

    # Projects
    user = User.objects.create(
        email="sample@user.com",
        password="sample-user",
        object_channel="default"
    )
    project1 = Project.objects.create(
        name="sample 1",
        owner=user,
        description="description",
        details="detail",
        object_channel="default",
        published=True
    )
    project1.categories.add(category1)
    job1 = Job.objects.create(project=project1, object_channel="default")
    date1 = JobDate.objects.create(
        job=job1,
        start_date=timezone.now(),
        end_date=timezone.now(),
        object_channel="default"
    )

    project2 = Project.objects.create(
        name="sample 2",
        owner=user,
        description="description",
        details="detail",
        object_channel="default",
        published=True
    )
    project2.categories.add(category2)
    job2 = Job.objects.create(project=project2, object_channel="default")
    date2 = JobDate.objects.create(
        job=job2,
        start_date=timezone.now() + relativedelta(days=3),
        end_date=timezone.now() + relativedelta(days=3),
        object_channel="default"
    )

    project3 = Project.objects.create(
        name="sample 3",
        owner=user,
        description="description",
        details="detail",
        object_channel="default",
        published=True
    )
    project3.categories.add(category3)
    job3 = Job.objects.create(project=project3, object_channel="default")
    date3 = JobDate.objects.create(
        job=job3,
        start_date=timezone.now() + relativedelta(weeks=1, days=1),
        end_date=timezone.now() + relativedelta(weeks=1, days=1),
        object_channel="default"
    )

    cache.clear()


class CatalogueCacheTestCase(TestCase):

    def setUp(self):
        setUp()
        self.client = APIClient()

    def test_get_catalogue_caching(self):
        with self.assertNumQueries(27):
            # 4 from catalogue, section and section filters models
            # 2 from category filters(section "hot")
            # 2 from category filters(section "get your hands dirty")
            # 2 from datedelta filters(section "coming up")
            response = self.client.get(
                reverse("catalogue", ["home"]),
                format="json"
            )
        self.assertEqual(len(response.data["sections"]), 3)

        with self.assertNumQueries(1):
            response2 = self.client.get(
                reverse("catalogue", ["home"]),
                format="json"
            )
        self.assertEqual(response.data, response2.data)

    def test_fetch_catalogue_num_queries(self):
        with self.assertNumQueries(27):
            # 4 from catalogue, section and section filters models
            # 2 from category filters(section "hot")
            # 2 from category filters(section "get your hands dirty")
            # 2 from datedelta filters(section "coming up")
            response = self.client.get(
                reverse("catalogue", ["home"]),
                format="json"
            )

    def test_fetch_queryset_without_serializer(self):
        request = self._generate_request()
        catalogue = get_catalogue("default", "home", request)
        fetched = fetch_catalogue(catalogue, request=request)
        self.assertEqual(
            fetched["sections"][0]["projects"].__class__,
            QuerySet
        )

    def test_fetch_queryset_with_serializer(self):
        request = self._generate_request()
        catalogue = get_catalogue("default", "home", request)
        fetched = fetch_catalogue(
            catalogue,
            request=request,
            serializer=ProjectSearchSerializer
        )
        self.assertEqual(
            fetched["sections"][0]["projects"].__class__,
            ReturnList
        )

    def _generate_request(self):
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        request.session = {}
        return request


class CatalogueViewTestCase(TestCase):

    def setUp(self):
        setUp()
        self.client = APIClient()

    def test_view_404(self):
        response = self.client.get(
            reverse("catalogue", ["invalid"]),
            format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_view_200(self):
        response = self.client.get(
            reverse("catalogue", ["home"]),
            format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_is_bookmarked(self):
        response = self.client.get(
            reverse("catalogue", ["home"]),
            format="json"
        )
        self.assertTrue(len(response.data["sections"]) > 0)
        sections = response.data["sections"]
        for project in sections[1]["projects"]:
            self.assertTrue("is_bookmarked" in project)
        for project in sections[2]["projects"]:
            self.assertTrue("is_bookmarked" in project)


class CategoryFilterTestCase(TestCase):

    def setUp(self):
        setUp()
        self.client = APIClient()

    def test_category_filter(self):
        response = self.client.get(
            reverse("catalogue", ["home"]),
            format="json"
        )

        test_section = list(
            filter(
                lambda x: x['name'] == 'Get your hands dirty',
                response.data["sections"]
            )
        )[0]
        self.assertEqual(len(test_section["projects"]), 1)
        self.assertEqual(
            test_section["projects"][0]["name"],
            "sample 2"
        )

        test_section = list(
            filter(
                lambda x: x['name'] == 'Hot',
                response.data["sections"]
            )
        )[0]
        self.assertEqual(len(test_section["projects"]), 1)
        self.assertEqual(
            test_section["projects"][0]["name"],
            "sample 1"
        )


class DateDeltaFilterTestCase(TestCase):

    def setUp(self):
        setUp()
        self.client = APIClient()

    def test_datedelta_filter(self):
        response = self.client.get(
            reverse("catalogue", ["home"]),
            format="json"
        )
        self.assertEqual(len(response.data["sections"][1]["projects"]), 1)
        self.assertEqual(
            response.data["sections"][1]["projects"][0]["name"],
            "sample 2"
        )
