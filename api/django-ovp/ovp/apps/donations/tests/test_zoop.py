import os

from django.test import TestCase
from django.test.utils import override_settings
from ovp.apps.donations.backends.zoop import ZoopBackend
from ovp.apps.donations.tests.helpers import card_token


class TestZoopBackend(TestCase):
    def setUp(self):
        self.backend = ZoopBackend()
        self.receiver = "feb6882b8e7b4b5cb59bf1e839555f25"

    def test_charge_card(self):
        token_id = card_token("5201561050024014")
        response = self.backend.charge(token_id, self.receiver, 100)
        self.assertEqual(response[0], 201)
        self.assertEqual(
            response[1], {
                "status": "succeeded", "message": "Transaction was authorized."})

    def test_cant_charge_token_twice(self):
        token_id = card_token("5201561050024014")
        response = self.backend.charge(token_id, self.receiver, 100)
        self.assertEqual(response[0], 201)
        self.assertEqual(
            response[1], {
                "status": "succeeded", "message": "Transaction was authorized."})

        response = self.backend.charge(token_id, self.receiver, 100)
        self.assertEqual(response[0], 404)
        self.assertEqual(
            response[1],
            {
                "status": "failed",
                "message": "Sorry, the token (id: {}) you are trying to use does not exist or has been deleted.".format(token_id),
                "category": "resource_not_found"})

    def test_invalid_card_number(self):
        token_id = card_token("6011457819940087")
        response = self.backend.charge(token_id, self.receiver, 100)
        self.assertEqual(response[0], 402)
        self.assertEqual(
            response[1],
            {
                "status": "failed",
                "message": "Your card was declined. For information about why your credit card was declined or rejected, please contact your bank or credit card vendor.",
                "category": "card_declined"})

    def test_expired_card(self):
        token_id = card_token("4929710426637678")
        response = self.backend.charge(token_id, self.receiver, 100)
        self.assertEqual(response[0], 402)
        self.assertEqual(
            response[1],
            {
                "status": "failed",
                "message": "Your card was declined. For information about why your credit card was declined or rejected, please contact your bank or credit card vendor.",
                "category": "card_declined"})

    def test_service_request_timeout(self):
        token_id = card_token("4710426743216178")
        response = self.backend.charge(token_id, self.receiver, 100)
        self.assertEqual(response[0], 408)
        self.assertEqual(
            response[1],
            {
                "status": "timeout",
                "message": "Credit card process is temporarily unavailable at the specified location. Please try again later. If the problem persists, please contact Technical Support (support@pagzoop.com).",
                "category": "service_request_timeout"})

    # Zoop is broken on this route
    # Card: 4556629972668582 should return "card declined"
    # Transaction succeeding instead
    # def test_card_declined(self):
    #  token_id = card_token("4556629972668582")
    #  response = self.backend.charge(token_id)
    #  self.assertEqual(response[0], 402)
    #  self.assertEqual(response[1], {"status": "failed", "message": "xxxx"})

    def test_create_plan(self):
        response = self.backend.create_plan(amount=100, interval=1)
        self.assertEqual(response[0], 201)
        self.assertEqual(response[1].json()["status"], "active")
        self.assertTrue(response[1].json()["id"])

    def test_attach_customer_to_token(self):
        self.backend.create_plan(amount=100, interval=1)
        token = self.backend.generate_card_token(
            holder_name="Test",
            expiration_month="03",
            expiration_year="2018",
            security_code="123",
            card_number="5201561050024014").json()["id"]
        customer = self.backend.create_customer(
            first_name="Abraham",
            last_name="Lincoln",
            description="Third sector donator",
            email="abrahamlincoln@usa.gov").json()["id"]
        response = self.backend.attach_token_to_customer(
            token=token, customer=customer)
        self.assertEqual(response[0], 200)
        self.assertTrue(response[1].json()["id"])

    def test_subscribe(self):
        plan = self.backend.create_plan(amount=100, interval=1)[1].json()["id"]
        token = self.backend.generate_card_token(
            holder_name="Test",
            expiration_month="03",
            expiration_year="2018",
            security_code="123",
            card_number="5201561050024014").json()["id"]
        customer = self.backend.create_customer(
            first_name="Abraham",
            last_name="Lincoln",
            description="Third sector donator",
            email="abrahamlincoln@usa.gov").json()["id"]
        self.backend.attach_token_to_customer(token=token, customer=customer)
        response = self.backend.subscribe_to_plan(plan=plan, customer=customer)
        # TODO: Amount none??? Test!
        self.assertEqual(response[0], 201)
        self.assertTrue(response[1].json()["status"], "active")

    def test_refund_transaction(self):
        token_id = card_token("5201561050024014")
        response = self.backend.charge(token_id, self.receiver, 100)
        transaction_id = response[2].json()["id"]
        response = self.backend.refund_transaction(transaction_id, self.receiver, 100)
        self.assertEqual(response[0], 200)
        self.assertTrue(response[1].json()["status"], "canceled")

    def test_list_sellers(self):
        response = self.backend.list_sellers()
        self.assertEqual(response[1].status_code, 200)
        self.assertTrue(response[1].json()["resource"] == "list")

    """
    Not used in production
    """

    def test_generate_card_token(self):
        response = self.backend.generate_card_token(
            holder_name="Test",
            expiration_month="03",
            expiration_year="2018",
            security_code="123",
            card_number="5201561050024014")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["id"])

    def test_create_customer(self):
        response = self.backend.create_customer(
            first_name="Abraham",
            last_name="Lincoln",
            description="Third sector donator",
            email="abrahamlincoln@usa.gov")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["id"])
