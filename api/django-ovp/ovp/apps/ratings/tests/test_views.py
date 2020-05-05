from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.users.models import User
from ovp.apps.projects.models import Project
from ovp.apps.organizations.models import Organization
from ovp.apps.ratings.models import RatingRequest
from ovp.apps.ratings.models import RatingParameter
from ovp.apps.ratings.models import Rating


class RatingViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="a",
            email="testmail@test.com",
            password="test_returned",
            object_channel="default")
        self.user2 = User.objects.create_user(
            name="b",
            email="testmail2@test.com",
            password="test_returned",
            object_channel="default")
        self.organization = Organization.objects.create(
            name="test org", owner=self.user, object_channel="default")
        self.project = Project.objects.create(
            name="test project",
            slug="test-slug",
            details="abc",
            description="abc",
            owner=self.user,
            organization=self.organization,
            published=False,
            object_channel="default")

        rp1 = RatingParameter.objects.create(
            slug="test-project-score", type=2, object_channel="default")
        rp2 = RatingParameter.objects.create(
            slug="test-project-how-was-it", type=1, object_channel="default")
        rp3 = RatingParameter.objects.create(
            slug="test-user-has-shown", type=3, object_channel="default")

        r1 = RatingRequest.objects.create(
            requested_user=self.user,
            rated_object=self.user,
            initiator_object=self.user,
            object_channel="default"
        )
        r2 = RatingRequest.objects.create(
            requested_user=self.user,
            rated_object=self.organization,
            initiator_object=self.user,
            object_channel="default"
        )
        r3 = RatingRequest.objects.create(
            requested_user=self.user,
            rated_object=self.project,
            initiator_object=self.user,
            object_channel="default"
        )

        r1.rating_parameters.add(rp3)
        r3.rating_parameters.add(rp1)
        r3.rating_parameters.add(rp2)

        self.client = APIClient()
        self.client.login(
            username="testmail@test.com",
            password="test_returned",
            channel="default"
        )

    def test_current_user_returns_rating_requests(self):
        response = self.client.get(
            reverse("user-current-user"), {}, format="json")
        self.assertEqual(response.data["rating_requests_user_count"], 1)

        self.client.force_authenticate(self.user2)
        response = self.client.get(
            reverse("user-current-user"), {}, format="json")
        self.assertEqual(response.data["rating_requests_user_count"], 0)

    def test_retrieve_rating_requests(self):
        response = APIClient().get(
            reverse("rating-request-list"),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.get(
            reverse("rating-request-list"), {}, format="json")
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["object_type"], "user")
        self.assertEqual(response.data[1]["object_type"], "organization")
        self.assertEqual(response.data[2]["object_type"], "project")

        self.client.force_authenticate(self.user2)
        response = self.client.get(
            reverse("user-current-user"),
            {},
            format="json"
        )
        self.assertEqual(response.data["rating_requests_user_count"], 0)

    def test_retrieve_rating_request_parameters(self):
        response = self.client.get(
            reverse("rating-request-list"), {}, format="json")
        self.assertEqual(len(response.data[0]["rating_parameters"]), 1)
        self.assertEqual(
            response.data[0]["rating_parameters"][0]["slug"],
            "test-user-has-shown")
        self.assertEqual(
            response.data[0]["rating_parameters"][0]["type"],
            "Boolean")

        self.assertEqual(len(response.data[2]["rating_parameters"]), 2)
        self.assertEqual(
            response.data[2]["rating_parameters"][0]["slug"],
            "test-project-score")
        self.assertEqual(
            response.data[2]["rating_parameters"][0]["type"],
            "Quantitative")
        self.assertEqual(
            response.data[2]["rating_parameters"][1]["slug"],
            "test-project-how-was-it")
        self.assertEqual(
            response.data[2]["rating_parameters"][1]["type"],
            "Qualitative")

    def test_cant_rate_if_not_requested(self):
        uuid = str(RatingRequest.objects.first().uuid)
        self.client.force_authenticate(self.user2)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            {},
            format="json")
        self.assertEqual(response.status_code, 404)

    def test_rate_validation(self):
        # Extra parameters
        data = {
            "answers": [
                {"parameter_slug": "test-project-score", "value_quantitative": 1},
                {
                    "parameter_slug": "test-project-how-was-it",
                    "value_qualitative": "test"
                },
                {
                    "parameter_slug": "project-dont-exist",
                    "value_quantitative": 1
                }
            ]
        }
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["non_field_errors"][0],
            "Invalid parameter 'project-dont-exist' for request.")

        # Duplicated parameters
        data = {
            "answers": [
                {"parameter_slug": "test-project-score", "value": 1},
                {"parameter_slug": "test-project-score", "value": 0.5},
                {"parameter_slug": "test-project-how-was-it", "value": "test"}
            ]
        }
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["non_field_errors"][0],
            "You have sent multiple answers for a parameter."
            " Check you request body."
        )

        # Missing parameters
        data = {
            "answers": [
            ]
        }
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["non_field_errors"][0],
            "The following parameters are missing: "
            "test-project-score, test-project-how-was-it."
        )

    def test_can_rate(self):
        data = {
            "answers": [
                {
                    "parameter_slug": "test-project-score",
                    "value_quantitative": 1
                },
                {
                    "parameter_slug": "test-project-how-was-it",
                    "value_qualitative": "Minha resposta :-)"
                }
            ]
        }
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Rating.objects.all().count(), 1)
        self.assertEqual(Rating.objects.first().owner, self.user)
        self.assertEqual(
            Rating.objects.first().request,
            RatingRequest.objects.last())
        self.assertEqual(Rating.objects.first().answers.count(), 2)

        self.assertEqual(
            Rating.objects.first().answers.first().parameter.slug,
            "test-project-score")
        self.assertEqual(
            Rating.objects.first().answers.first().value_quantitative, 1)

        self.assertEqual(
            Rating.objects.first().answers.last().parameter.slug,
            "test-project-how-was-it")
        self.assertEqual(
            Rating.objects.first().answers.last().value_qualitative,
            "Minha resposta :-)")

    def test_cant_re_rate(self):
        self.test_can_rate()
        data = {"answers": [{"parameter_slug": "test-project-score",
                             "value_quantitative": 1},
                            {"parameter_slug": "test-project-how-was-it",
                             "value_qualitative": "Minha resposta :-)"}]}
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]
            ),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not found.")

    def test_quantitative(self):
        data = {
            "answers": [
                {
                    "parameter_slug": "test-project-score",
                    "value_quantitative": 2
                },
                {
                    "parameter_slug": "test-project-how-was-it",
                    "value_qualitative": "Minha resposta :-)"
                }
            ]
        }
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['answers'][0]['non_field_errors'][0],
            "'value_quantitative' must be between 0 and 1 for "
            "qualitative parameters."
        )

        data = {
            "answers": [
                {"parameter_slug": "test-project-score", "value_quantitative": -1},
                {
                    "parameter_slug": "test-project-how-was-it",
                    "value_qualitative": "Minha resposta :-)"
                }
            ]
        }
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 400)

        data = {
            "answers": [
                {"parameter_slug": "test-project-score", "value_quantitative": 0.5},
                {
                    "parameter_slug": "test-project-how-was-it",
                    "value_qualitative": "Minha resposta :-)"
                }
            ]
        }
        uuid = str(RatingRequest.objects.last().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 200)

    def test_boolean(self):
        data = {
            "answers": [
                {
                    "parameter_slug": "test-user-has-shown",
                    "value_quantitative": 0.5
                },
            ]
        }
        uuid = str(RatingRequest.objects.first().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['answers'][0]['non_field_errors'][0],
            "'value_quantitative' must be 0 or 1 for boolean parameters.")

        data = {
            "answers": [
                {"parameter_slug": "test-user-has-shown", "value_quantitative": 1},
            ]
        }
        uuid = str(RatingRequest.objects.first().uuid)
        response = self.client.post(
            reverse(
                "rating-request-rate",
                [uuid]),
            data,
            format="json")
        self.assertEqual(response.status_code, 200)
