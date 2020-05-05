import requests
from django.utils import timezone
from django.conf import settings
from ovp.apps.donations.backends.base import BaseBackend

POST = "post"
GET = "get"
PATCH = "patch"
PUT = "put"
DELETE = "delete"

class ZoopBackend(BaseBackend):
    name = "zoop"
    def __init__(self):
        self.marketplace_id = getattr(settings, "ZOOP_MARKETPLACE_ID", None)
        self.pub_key = getattr(settings, "ZOOP_PUB_KEY", None)
        self.seller_id = getattr(settings, "ZOOP_SELLER_ID", None)
        self.statement_descriptor = getattr(
            settings, "ZOOP_STATEMENT_DESCRIPTOR", None)

    def _build_url(self, resource):
        return "https://api.zoop.ws/" + \
            resource.format(mpid=self.marketplace_id)

    def _assert_keys(self):
        assert (self.marketplace_id and self.pub_key and
                self.seller_id and self.statement_descriptor)

    def call(self, http_method, resource, data={}):
        self._assert_keys()
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        kwargs = {
            'auth': (self.pub_key, ''),
            'headers': headers,
        }

        if data:
            kwargs['json'] = data

        call_method = getattr(requests, http_method)
        url = self._build_url(resource)
        response = call_method(url, **kwargs)
        return response

    def charge(self, token, receiver, amount):
        data = {
            "payment_type": "credit",
            "currency": "BRL",
            "description": "donation",
            "amount": 100,
            "on_behalf_of": receiver,
            "statement_descriptor": self.statement_descriptor,
            "token": token,
            "split_rules": [
              {
                "recipient": self.seller_id,
                "liable": 1,
                "charge_processing_fee": 1,
                "percentage": 10,
                "amount": 0
              },
            ]
        }
        response = self.call(POST, "v1/marketplaces/{mpid}/transactions", data)
        try:
            response_data = response.json()
        except BaseException:
            pass

        if response.status_code in [200, 201]:
            return (
                response.status_code, {
                    "status": "succeeded", "message": "Transaction was authorized."}, response)

        if response.status_code in [400, 401]:
            return (response.status_code,
                    {"status": "failed",
                     "message": "An internal error occurred during processing."},
                    response)

        if response.status_code == 402:
            return (response.status_code,
                    {"status": "failed",
                     "message": response_data["error"]["message"],
                     "category": response_data["error"]["category"]},
                    response)

        if response.status_code == 404:
            return (response.status_code,
                    {"status": "failed",
                     "message": response_data["error"]["message"],
                     "category": response_data["error"]["category"]},
                    response)

        if response.status_code == 408:
            return (response.status_code,
                    {"status": "timeout",
                     "message": response_data["error"]["message"],
                     "category": response_data["error"]["category"]},
                    response)

        if response.status_code in [403, 500, 502]:
            return (500,
                    {"status": "error",
                     "message": "Internal error occurred. This issue is being investigated."},
                    response)

        return (500,
                {"status": "error",
                 "message": "An unexpected error occurred. This issue is being investigated."},
                response)

    def refund_transaction(self, transaction_id, seller_id, amount):
        data = {
            "amount": amount,
            "on_behalf_of": seller_id,
        }
        response = self.call(
            POST, "v1/marketplaces/{mpid}/transactions/{transaction_id}/void".format(
                mpid="{mpid}", transaction_id=transaction_id), data)
        return (response.status_code, response)

    def create_plan(self, amount, interval=1):
        data = {
            "frequency": "monthly",
            "interval": interval,
            "payment_methods": ["credit"],
            "name": "Plano mensal ({})".format(amount),
            "setup_amount": 0,
            "currency": "BRL",
            "amount": amount
        }
        response = self.call(POST, "v2/marketplaces/{mpid}/plans", data)
        return (response.status_code, response)

    def subscribe_to_plan(self, plan, customer):
        data = {
            "currency": "BRL",
            "on_behalf_of": self.seller_id,
            "customer": customer,
            "plan": plan,
            "due_date": timezone.now().strftime("%Y-%m-%d")
        }
        response = self.call(
            POST, "v2/marketplaces/{mpid}/subscriptions", data)
        return (response.status_code, response)

    def attach_token_to_customer(self, token, customer):
        data = {
            "token": token,
            "customer": customer
        }
        response = self.call(POST, "v1/marketplaces/{mpid}/cards", data)
        return (response.status_code, response)

    def list_sellers(self):
        response = self.call(GET, "v1/marketplaces/{mpid}/sellers")
        return (response.status_code, response)

    """"
    The following methods are not used in production. They are only used in the test suite to
    These routes should be called from the front-end.
    """

    def generate_card_token(self,
                            holder_name=None,
                            expiration_month=None,
                            expiration_year=None,
                            security_code=None,
                            card_number=None):
        data = {
            "holder_name": holder_name,
            "expiration_month": expiration_month,
            "expiration_year": expiration_year,
            "security_code": security_code,
            "card_number": card_number
        }
        return self.call(POST, "v1/marketplaces/{mpid}/cards/tokens", data)

    def create_customer(self,
                        first_name=None,
                        last_name=None,
                        description=None,
                        email=None):
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "description": description,
            "email": email
        }
        return self.call(POST, "v1/marketplaces/{mpid}/buyers", data)
