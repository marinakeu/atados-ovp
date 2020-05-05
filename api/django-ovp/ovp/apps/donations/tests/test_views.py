import os

from collections import OrderedDict

from django.test import TestCase
from django.test.utils import override_settings

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.users.models import User
from ovp.apps.organizations.models import Organization
from ovp.apps.donations.models import Transaction
from ovp.apps.donations.models import Subscription
from ovp.apps.donations.models import Seller
from ovp.apps.donations.backends.zoop import ZoopBackend
from ovp.apps.donations.tests.helpers import card_token


class TestDonationsViewSet(TestCase):
    def setUp(self):
        self.backend = ZoopBackend()
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="a",
            email="testmail-projects@test.com",
            password="test_returned",
            object_channel="default")
        self.donator = User.objects.create_user(
            name="a",
            email="donator@test.com",
            password="test_returned",
            object_channel="default")
        self.non_donator = User.objects.create_user(
            name="a",
            email="non_donator@test.com",
            password="test_returned",
            object_channel="default")
        self.organization = Organization.objects.create(
            name="test org",
            owner=self.user,
            object_channel="default",
            allow_donations=True)

        self.data = {
            "organization_id": self.organization.id,
            "amount": 100,
            "token": "invalid"
        }

        Seller.objects.create(
            object_channel="default",
            organization=self.organization,
            backend="zoop",
            seller_id="feb6882b8e7b4b5cb59bf1e839555f25"
        )

    def test_cant_donate_unauthenticated(self):
        response = self.client.post(reverse("donation-donate"), format="json")
        self.assertEqual(response.status_code, 401)

    def test_cant_donate_if_organization_not_flagged(self):
        self.organization.allow_donations = False
        self.organization.save()
        self.client.force_authenticate(user=self.donator)

        response = self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                'organization_id': [
                    "Organization with 'id' {} and 'allow_donations' True does not exist.".format(
                        self.organization.pk)]})

    def test_can_donate(self):
        self.client.force_authenticate(user=self.donator)
        self.data["token"] = card_token("5201561050024014")

        self.assertEqual(Transaction.objects.all().count(), 0)

        response = self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data, {
                'status': 'succeeded', 'message': 'Transaction was authorized.'})

        self.assertEqual(Transaction.objects.all().count(), 1)
        transaction = Transaction.objects.last()
        self.assertEqual(transaction.user, self.donator)
        self.assertEqual(transaction.organization, self.organization)
        self.assertEqual(transaction.amount, self.data["amount"])
        self.assertEqual(transaction.status, "succeeded")
        self.assertEqual(transaction.message, "Transaction was authorized.")
        self.assertTrue(transaction.backend_transaction_id)
        self.assertTrue(transaction.backend_transaction_number)
        self.assertEqual(transaction.anonymous, False)

    def test_can_donate_anonymously(self):
        self.client.force_authenticate(user=self.donator)
        self.data["token"] = card_token("5201561050024014")
        self.data["anonymous"] = True

        self.assertEqual(Transaction.objects.all().count(), 0)

        response = self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data, {
                'status': 'succeeded', 'message': 'Transaction was authorized.'})

        self.assertEqual(Transaction.objects.all().count(), 1)
        transaction = Transaction.objects.last()
        self.assertEqual(transaction.user, self.donator)
        self.assertEqual(transaction.organization, self.organization)
        self.assertEqual(transaction.amount, self.data["amount"])
        self.assertEqual(transaction.status, "succeeded")
        self.assertEqual(transaction.message, "Transaction was authorized.")
        self.assertTrue(transaction.backend_transaction_id)
        self.assertTrue(transaction.backend_transaction_number)
        self.assertEqual(transaction.anonymous, True)

    def test_cant_donate_negative(self):
        self.client.force_authenticate(user=self.donator)
        self.data["token"] = card_token("5201561050024014")
        self.data["amount"] = -100

        response = self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                'amount': ['Ensure this value is greater than or equal to 1.']})

    def test_cant_donate_invalid_card(self):
        self.client.force_authenticate(user=self.donator)

        self.data["token"] = card_token("6011457819940087")
        response = self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 402)
        self.assertEqual(
            response.data,
            {
                "status": "failed",
                "message": "Your card was declined. For information about why your credit card was declined or rejected, please contact your bank or credit card vendor.",
                "category": "card_declined"})

        self.data["token"] = card_token("4929710426637678")
        response = self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 402)
        self.assertEqual(
            response.data,
            {
                "status": "failed",
                "message": "Your card was declined. For information about why your credit card was declined or rejected, please contact your bank or credit card vendor.",
                "category": "card_declined"})

    def test_cant_donate_timeout(self):
        self.client.force_authenticate(user=self.donator)

        self.data["token"] = card_token("4710426743216178")
        response = self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 408)
        self.assertEqual(
            response.data,
            {
                "status": "timeout",
                "message": "Credit card process is temporarily unavailable at the specified location. Please try again later. If the problem persists, please contact Technical Support (support@pagzoop.com).",
                "category": "service_request_timeout"})

    def test_can_retrieve_transactions(self):
        response = self.client.get(
            reverse("donation-transactions"), format="json")
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.donator)
        response = self.client.get(
            reverse("donation-transactions"), format="json")
        self.assertEqual(response.data["count"], 0)
        self.test_can_donate()
        response = self.client.get(
            reverse("donation-transactions"), format="json")
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["uuid"])
        self.assertEqual(response.data["results"][0]["amount"], 100)
        self.assertEqual(response.data["results"][0]["status"], "succeeded")
        self.assertTrue(
            isinstance(
                response.data["results"][0]["organization"],
                OrderedDict))

        self.client.force_authenticate(user=self.non_donator)
        response = self.client.get(
            reverse("donation-transactions"), format="json")
        self.assertEqual(response.data["count"], 0)

    def test_can_refund_transaction(self):
        self.test_can_donate()
        data = {"uuid": Transaction.objects.last().uuid}

        response = self.client.post(
            reverse("donation-refund-transaction"),
            data=data,
            format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transaction.objects.last().status, "canceled")

    def test_cant_refund_unauthenticated(self):
        self.test_can_donate()
        data = {"uuid": Transaction.objects.last().uuid}

        response = APIClient().post(
            reverse("donation-refund-transaction"),
            data=data,
            format="json")
        self.assertEqual(response.status_code, 401)

    def test_cant_refund_if_not_succeeded(self):
        self.test_can_donate()
        transaction = Transaction.objects.last()
        transaction.status = "failed"
        transaction.save()
        data = {"uuid": transaction.uuid}

        response = self.client.post(
            reverse("donation-refund-transaction"),
            data=data,
            format="json")
        self.assertEqual(response.status_code, 404)

    def test_cant_refund_if_not_owner(self):
        self.test_can_donate()
        data = {"uuid": Transaction.objects.last().uuid}
        self.client.force_authenticate(user=self.non_donator)

        response = self.client.post(
            reverse("donation-refund-transaction"),
            data=data,
            format="json")
        self.assertEqual(response.status_code, 404)

    # Zoop broken for this operation
    # def test_cant_donate_card_declined(self):
    #  self.client.force_authenticate(user=self.donator)
    #
    #  self.data["token"] = card_token("4556629972668582")
    #  response = self.client.post(reverse("donation-donate"), data=self.data, format="json")
    #  self.assertEqual(response.status_code, 402)
    #  self.assertEqual(response.data, {"status": "failed", "message": "xxxxx", "category": "card_declined"})


class TestSubscriptionViewSet(TestCase):
    def setUp(self):
        self.backend = ZoopBackend()
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="a",
            email="testmail-projects@test.com",
            password="test_returned",
            object_channel="default")
        self.donator = User.objects.create_user(
            name="a",
            email="donator@test.com",
            password="test_returned",
            object_channel="default")
        self.non_donator = User.objects.create_user(
            name="a",
            email="non_donator@test.com",
            password="test_returned",
            object_channel="default")
        self.organization = Organization.objects.create(
            name="test org",
            owner=self.user,
            object_channel="default",
            allow_donations=True)

        self.data = {
            "organization_id": self.organization.id,
            "amount": 100,
            "token": "invalid",
            "customer": "invalid",
            "interval": 1
        }

    def test_cant_subscribe_unauthenticated(self):
        response = self.client.post(
            reverse("donation-subscribe"), format="json")
        self.assertEqual(response.status_code, 401)

    def test_cant_subscribe_if_organization_not_flagged(self):
        self.organization.allow_donations = False
        self.organization.save()
        self.client.force_authenticate(user=self.donator)

        response = self.client.post(
            reverse("donation-subscribe"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {
                'organization_id': [
                    "Organization with 'id' {} and 'allow_donations' True does not exist.".format(
                        self.organization.id)]})

    def test_can_subscribe(self):
        self.client.force_authenticate(user=self.donator)
        self.data["token"] = card_token("5201561050024014")
        self.data["customer"] = self.backend.create_customer(
            first_name="Abraham",
            last_name="Lincoln",
            description="Third sector donator",
            email="abrahamlincoln@usa.gov").json()["id"]

        self.assertEqual(Subscription.objects.all().count(), 0)

        response = self.client.post(
            reverse("donation-subscribe"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subscription.objects.all().count(), 1)

        subscription = Subscription.objects.last()
        self.assertEqual(subscription.amount, self.data["amount"])
        self.assertEqual(subscription.organization, self.organization)
        self.assertEqual(subscription.user, self.donator)
        self.assertEqual(subscription.status, "active")
        self.assertEqual(subscription.anonymous, False)

    def test_can_subscribe_anonymously(self):
        self.client.force_authenticate(user=self.donator)
        self.data["token"] = card_token("5201561050024014")
        self.data["customer"] = self.backend.create_customer(
            first_name="Abraham",
            last_name="Lincoln",
            description="Third sector donator",
            email="abrahamlincoln@usa.gov").json()["id"]
        self.data["anonymous"] = True

        self.assertEqual(Subscription.objects.all().count(), 0)

        response = self.client.post(
            reverse("donation-subscribe"),
            data=self.data,
            format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Subscription.objects.all().count(), 1)

        subscription = Subscription.objects.last()
        self.assertEqual(subscription.amount, self.data["amount"])
        self.assertEqual(subscription.organization, self.organization)
        self.assertEqual(subscription.user, self.donator)
        self.assertEqual(subscription.status, "active")
        self.assertEqual(subscription.anonymous, True)

    def test_can_retrieve_subscriptions(self):
        self.client.force_authenticate(user=self.donator)
        response = self.client.get(reverse("donation-subscriptions"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

        self.test_can_subscribe()
        response = self.client.get(reverse("donation-subscriptions"))
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(len(response.json()["results"]), 1)

    def test_cant_retrieve_not_your_subscriptions(self):
        response = self.client.get(reverse("donation-subscriptions"))
        self.assertEqual(response.status_code, 401)

        self.test_can_subscribe()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("donation-subscriptions"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

    def test_can_cancel_subscription(self):
        self.assertEqual(Subscription.objects.count(), 0)
        self.test_can_subscribe()
        subscription = Subscription.objects.last()

        data = {
            "uuid": subscription.uuid
        }
        response = self.client.post(
            reverse("donation-cancel-subscription"),
            data=data,
            format="json")
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            response.json(), {
                "success": True, "status": "canceled"})

        response = self.client.post(
            reverse("donation-cancel-subscription"),
            data=data,
            format="json")
        self.assertTrue(response.status_code, 404)

    def test_cant_cancel_not_your_subscription(self):
        self.assertEqual(Subscription.objects.count(), 0)
        self.test_can_subscribe()
        subscription = Subscription.objects.last()

        data = {
            "uuid": subscription.uuid
        }
        response = APIClient().post(
            reverse("donation-cancel-subscription"),
            data=data,
            format="json")
        self.assertTrue(response.status_code, 401)
        self.client.force_authenticate(user=self.non_donator)
        response = APIClient().post(
            reverse("donation-cancel-subscription"),
            data=data,
            format="json")
        self.assertTrue(response.status_code, 404)

    # Zoop returns valid subscription
    # TODO: check
    # def test_cant_subscribe_invalid_card(self):
    #  self.client.force_authenticate(user=self.donator)
    #  self.data["token"] = card_token("6011457819940087")
    #  self.data["customer"] = self.backend.create_customer(first_name="Abraham", last_name="Lincoln", description="Third sector donator", email="abrahamlincoln@usa.gov").json()["id"]

    #  self.assertEqual(Subscription.objects.all().count(), 0)

    #  response = self.client.post(reverse("donation-subscribe"), data=self.data, format="json")
    #  import pudb;pudb.set_trace()
    #  self.assertEqual(response.status_code, 201)
    #  self.assertEqual(Subscription.objects.all().count(), 1)


class TestPublicUserDonationListing(TestCase):
    def setUp(self):
        self.backend = ZoopBackend()
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="a",
            email="testmail-projects@test.com",
            password="test_returned",
            object_channel="default")
        self.donator = User.objects.create_user(
            name="a",
            email="donator@test.com",
            password="test_returned",
            object_channel="default")
        self.organization = Organization.objects.create(
            name="test org",
            owner=self.user,
            object_channel="default",
            allow_donations=True)
        self.organization_received_anonymously = Organization.objects.create(
            name="test org received anonymously",
            owner=self.user,
            object_channel="default",
            allow_donations=True)

        Seller.objects.create(
            object_channel="default",
            organization=self.organization,
            backend="zoop",
            seller_id="feb6882b8e7b4b5cb59bf1e839555f25"
        )

        Seller.objects.create(
            object_channel="default",
            organization=self.organization_received_anonymously,
            backend="zoop",
            seller_id="feb6882b8e7b4b5cb59bf1e839555f25"
        )

        self.data = {
            "organization_id": self.organization.id,
            "amount": 100,
            "token": "invalid"
        }

    def test_organizations_are_shown_on_public_user(self):
        self.client.force_authenticate(user=self.donator)
        self.data["token"] = card_token("5201561050024014")
        self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")

        client = APIClient()
        response = client.get(
            reverse('public-users-detail', [self.donator.slug]), format="json")

        self.assertEqual(len(response.data['donated_to_organizations']), 1)
        self.assertEqual(
            response.data['donated_to_organizations'][0]['slug'],
            self.organization.slug)

    def test_anonymous_donations_are_not_shown_on_public_user(self):
        self.client.force_authenticate(user=self.donator)
        self.data["token"] = card_token("5201561050024014")
        self.data["organization_id"] = self.organization_received_anonymously.pk
        self.data["anonymous"] = True
        self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")

        client = APIClient()
        response = client.get(
            reverse('public-users-detail', [self.donator.slug]), format="json")


        self.assertEqual(
            self.organization_received_anonymously.transaction_set.count(), 1)
        self.assertEqual(len(response.data['donated_to_organizations']), 0)


class TestOrganizationDonationListing(TestCase):
    def setUp(self):
        self.backend = ZoopBackend()
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="a",
            email="testmail-projects@test.com",
            password="test_returned",
            object_channel="default")
        self.donator = User.objects.create_user(
            name="a",
            email="donator@test.com",
            password="test_returned",
            object_channel="default")
        self.donator_anon = User.objects.create_user(
            name="a",
            email="donatoranon@test.com",
            password="test_returned",
            object_channel="default")
        self.organization = Organization.objects.create(
            name="test org",
            owner=self.user,
            object_channel="default",
            allow_donations=True)
        Seller.objects.create(
            object_channel="default",
            organization=self.organization,
            backend="zoop",
            seller_id="feb6882b8e7b4b5cb59bf1e839555f25"
        )

        self.data = {
            "organization_id": self.organization.id,
            "amount": 100,
            "token": card_token("5201561050024014")
        }

    def test_donators_are_shown_at_organization_route(self):
        self.client.force_authenticate(user=self.donator)
        c=self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")

        client = APIClient()
        response = client.get(
            reverse("organization-detail", [self.organization.slug]), format="json")

        self.assertTrue("donators" in response.data)
        self.assertEqual(
            response.data['donators'][0]['slug'],
            self.donator.slug)

    def test_anonymous_donators_are_hidden_at_organization_route(self):
        self.client.force_authenticate(user=self.donator)
        self.data['anonymous'] = True
        self.client.post(
            reverse("donation-donate"),
            data=self.data,
            format="json")

        client = APIClient()
        response = client.get(
            reverse("organization-detail", [self.organization.slug]), format="json")

        self.assertTrue("donators" in response.data)
        self.assertEqual(len(response.data['donators']), 0)
        self.assertEqual(self.organization.transaction_set.count(), 1)
