from django.shortcuts import get_object_or_404

from ovp.apps.channels.viewsets.decorators import ChannelViewSet
from ovp.apps.donations.backends.zoop import ZoopBackend
from ovp.apps.donations.models import Transaction
from ovp.apps.donations.models import Subscription
from ovp.apps.organizations.models import Organization

from ovp.apps.donations.serializers import DonateSerializer
from ovp.apps.donations.serializers import TransactionRetrieveSerializer
from ovp.apps.donations.serializers import RefundTransactionSerializer
from ovp.apps.donations.serializers import SubscribeSerializer
from ovp.apps.donations.serializers import SubscriptionRetrieveSerializer
from ovp.apps.donations.serializers import CancelSubscriptionSerializer

from rest_framework import viewsets
from rest_framework import decorators
from rest_framework import response
from rest_framework import permissions

@ChannelViewSet
class DonationViewSet(viewsets.GenericViewSet):
    # POST /subscribe/
    # GET /subscriptions/
    # DELETE /subscription/

    def __init__(self, *args, **kwargs):
        self.backend = ZoopBackend()
        return super(DonationViewSet, self).__init__()

    def get_queryset(self, *args, **kwargs):
        if self.action in ["transactions", "refund_transaction"]:
            return Transaction.objects.filter(
                user=self.request.user).order_by("-pk")
        if self.action in [
            "subscribe",
            "subscriptions",
                "cancel_subscription"]:
            return Subscription.objects.filter(
                user=self.request.user).order_by("-pk")
        return None

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "donate":
            return DonateSerializer
        if self.action == "transactions":
            return TransactionRetrieveSerializer
        if self.action == "refund_transaction":
            return RefundTransactionSerializer
        if self.action == "subscribe":
            return SubscribeSerializer
        if self.action == "subscriptions":
            return SubscriptionRetrieveSerializer
        if self.action == "cancel_subscription":
            return SubscriptionRetrieveSerializer

    def get_permissions(self):
        if self.action == "donate":
            self.permission_classes = (permissions.IsAuthenticated,)
        if self.action == "transactions":
            self.permission_classes = (permissions.IsAuthenticated,)
        if self.action == "refund_transaction":
            self.permission_classes = (permissions.IsAuthenticated,)
        if self.action == "subscribe":
            self.permission_classes = (permissions.IsAuthenticated,)
        if self.action == "subscriptions":
            self.permission_classes = (permissions.IsAuthenticated,)
        if self.action == "cancel_subscription":
            self.permission_classes = (permissions.IsAuthenticated,)
        return super(DonationViewSet, self).get_permissions()

    ##################
    # ViewSet routes #
    ##################
    @decorators.action(methods=["POST"], detail=False)
    def donate(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        organization = get_object_or_404(
            Organization.objects,
            pk=data["organization_id"],
            channel__slug=self.request.channel
        )
        seller = organization.get_seller_object(self.backend.name)
        if not organization.allow_donations or not seller:
            return response.Response(
                {"success": False,
                 "message": "Organization is not enabled for donations."},
                status=400)

        charge_data = self.backend.charge(
            token=data["token"], receiver=seller.seller_id, amount=data["amount"])
        backend_response_data = charge_data[2].json()

        Transaction.objects.create(
            user=self.request.user,
            organization=Organization.objects.get(
                pk=data["organization_id"]),
            amount=data["amount"],
            status=charge_data[1]["status"],
            message=charge_data[1]["message"],
            backend_transaction_id=backend_response_data.get(
                "id",
                None),
            backend_transaction_number=backend_response_data.get(
                "transaction_number",
                None),
            anonymous=data.get(
                "anonymous",
                False),
            object_channel=request.channel)

        return response.Response(charge_data[1], status=charge_data[0])

    @decorators.action(methods=["GET"], detail=False)
    def transactions(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @decorators.action(methods=["POST"], detail=False)
    def refund_transaction(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(
            queryset,
            uuid=serializer.data["uuid"],
            status="succeeded")
        seller = obj.organization.get_seller_object(self.backend.name)

        status, backend_response = self.backend.refund_transaction(
            obj.backend_transaction_id, seller.seller_id, obj.amount)
        if status != 200:
            return response.Response(
                {"success": False, "message": "Internal error ocurred."}, status=500)

        obj.status = backend_response.json()["status"]
        obj.save()

        return response.Response({"success": True, "status": "canceled"})

    @decorators.action(methods=["POST"], detail=False)
    def subscribe(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        plan = self.backend.create_plan(
            amount=data["amount"],
            interval=data["interval"])[1].json()["id"]
        self.backend.attach_token_to_customer(
            token=data["token"], customer=data["customer"])
        status, subscribe_response = self.backend.subscribe_to_plan(
            plan=plan, customer=data["customer"])
        response_data = subscribe_response.json()

        if status == 201 and response_data["status"] == "active":
            Subscription.objects.create(
                user=request.user,
                organization=Organization.objects.get(
                    pk=data["organization_id"]),
                amount=data["amount"],
                status=response_data["status"],
                backend_subscription_id=response_data["id"],
                backend_plan_id=plan,
                anonymous=data.get(
                    "anonymous",
                    False),
                object_channel=request.channel,
            )

        return response.Response(response_data, status=status)

       # TODO: finish, check for errors
       # TODO: Integrate seller_id and splitting

    @decorators.action(methods=["GET"], detail=False)
    def subscriptions(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @decorators.action(methods=["POST"], detail=False)
    def cancel_subscription(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(
            queryset,
            uuid=serializer.data["uuid"],
            status="active")

        # TODO: Implement backend
        #status, backend_response = self.backend.refund_transaction(obj.backend_transaction_id, obj.amount)
        # if status != 200:
        # return response.Response({"success": False, "message": "Internal
        # error ocurred."}, status=500)

        obj.status = "canceled"
        obj.save()

        return response.Response({"success": True, "status": "canceled"})
