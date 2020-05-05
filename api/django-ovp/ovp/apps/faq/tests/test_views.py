from collections import OrderedDict
from django.test import TestCase

from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.faq.views.faq import FaqResourceViewSet

from ovp.apps.channels.models import Channel
from ovp.apps.faq.models.category import FaqCategory
from ovp.apps.faq.models.faq import Faq


class FaqResourceViewSetTestCase(TestCase):
    """
    Class responsible for applying all tests in FAQ views
    and displaying their results.
    """
    def setUp(self):
        self.client = APIClient()
        self.endpoint = reverse("faq-list")

        category_1 = FaqCategory.objects.create(
            name='Institucionais',
            object_channel="default"
        )
        question_1 = Faq.objects.create(
            question="Quem é o Atados?",
            answer="O Atados é uma plataforma social online que conecta "
            "pessoas à oportunidades de voluntariado em causas sociais.",
            category=category_1,
            language='pt-BR',
            object_channel="default"
        )

        category_2 = FaqCategory.objects.create(
            name='Comerciais',
            object_channel="default"
        )
        question_2 = Faq.objects.create(
            question='Há quanto tempo a atados está no mercado?',
            answer='A Atados está atuando no mercado há mais de 7 anos.',
            category=category_2,
            language='pt-BR',
            object_channel="default"
        )

        Channel.objects.create(slug="test-channel")

        category_3 = FaqCategory.objects.create(
            name='Institucionais',
            object_channel="test-channel"
        )
        question_3 = Faq.objects.create(
            question="Quem é o Atados?",
            answer="O Atados é uma plataforma social online que conecta "
            "pessoas à oportunidades de voluntariado em causas sociais.",
            category=category_3,
            language='pt-BR',
            object_channel="test-channel"
        )

    def test_list_status_200(self):
        # Opening get request with faq listing
        response = self.client.get(self.endpoint, {}, format="json")
        self.assertEqual(response.status_code, 200)

    def test_list_reject_post_method(self):
        # Opening post request with faq listing
        response = self.client.post(self.endpoint, {}, format="json")

        # Ensuring that post method will be rejected
        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            response.json(),
            {
                'detail': 'Method "POST" not allowed.'
            }
        )

    def test_list_check_queryset_channel_default(self):
        # Opening get request with faq listing
        response = self.client.get(self.endpoint, {}, format="json")

        # Ensuring the right number of questions
        self.assertEqual(len(response.data), 2)

        # Checking the registration of question 1
        self.assertTrue(
            OrderedDict(
                {
                    "id": 1,
                    "question": "Quem é o Atados?",
                    "answer": "O Atados é uma plataforma social online que "
                              "conecta pessoas à oportunidades de "
                              "voluntariado em causas sociais.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 1, "name": "Institucionais"}
                    )
                }
            )
            in response.data
        )

        # Checking the registration of question 2
        self.assertTrue(
            OrderedDict(
                {
                    "id": 2,
                    "question": "Há quanto tempo a atados está no mercado?",
                    "answer": "A Atados está atuando no mercado "
                              "há mais de 7 anos.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 2, "name": "Comerciais"}
                    )
                }
            )
            in response.data
        )

        # Verifying that the registration
        # for question 3 did not come in default
        self.assertFalse(
            OrderedDict(
                {
                    "id": 3,
                    "question": "Quem é o Atados?",
                    "answer": "O Atados é uma plataforma social online "
                              "que conecta pessoas à oportunidades de "
                              "voluntariado em causas sociais.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 3, "name": "Institucionais"}
                    )
                }
            )
            in response.data
        )

    def test_list_check_queryset_channel_test_channel(self):
        # Opening get request with faq listing
        response = self.client.get(
            self.endpoint,
            format="json",
            HTTP_X_OVP_CHANNEL="test-channel"
        )

        # Ensuring the right number of questions
        self.assertEqual(len(response.data), 1)

        # Verifying that the registration
        # for question 1 did not come in default
        self.assertFalse(
            OrderedDict(
                {
                    "id": 1,
                    "question": "Quem é o Atados?",
                    "answer": "O Atados é uma plataforma social online que "
                              "conecta pessoas à oportunidades de "
                              "voluntariado em causas sociais.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 1, "name": "Institucionais"}
                    )
                }
            )
            in response.data
        )

        # Verifying that the registration
        # for question 2 did not come in default
        self.assertFalse(
            OrderedDict(
                {
                    "id": 2,
                    "question": "Há quanto tempo a atados está no mercado?",
                    "answer": "A Atados está atuando no mercado "
                              "há mais de 7 anos.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 2, "name": "Comerciais"}
                    )
                }
            )
            in response.data
        )

        # Checking the registration of question 3
        self.assertTrue(
            OrderedDict(
                {
                    "id": 6,
                    "question": "Quem é o Atados?",
                    "answer": "O Atados é uma plataforma social online "
                              "que conecta pessoas à oportunidades de "
                              "voluntariado em causas sociais.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 6, "name": "Institucionais"}
                    )
                }
            )
            in response.data
        )

    def test_list_check_queryset_filters(self):
        # Opening get request with faq listing applying filters
        data_1 = {
            'category': "7",  # Institucionais
            'language': 'pt-BR',
        }
        response_1 = self.client.get(self.endpoint, data_1, format="json")

        data_2 = {
            'category': "8",  # Comerciais
            'language': 'pt-BR',
        }
        response_2 = self.client.get(self.endpoint, data_2, format="json")

        # Ensuring the right number of questions applied filters
        self.assertEqual(len(response_1.data), 1)
        self.assertFalse(
            OrderedDict(
                {
                    "id": 1,
                    "question": "Quem é o Atados?",
                    "answer": "O Atados é uma plataforma social online que "
                              "conecta pessoas à oportunidades de "
                              "voluntariado em causas sociais.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 7, "name": "Institucionais"}
                    )
                }
            )
            in response_1.data
        )

        self.assertEqual(len(response_2.data), 1)
        self.assertFalse(
            OrderedDict(
                {
                    "id": 2,
                    "question": "Há quanto tempo a atados está no mercado?",
                    "answer": "A Atados está atuando no mercado "
                              "há mais de 7 anos.",
                    "language": "pt-BR",
                    "category": OrderedDict(
                        {"id": 8, "name": "Comerciais"}
                    )
                }
            )
            in response_2.data
        )
