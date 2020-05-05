from rest_framework import serializers
from ovp.apps.donations.validators import organization_accepts_donations
from ovp.apps.donations.models import Transaction
from ovp.apps.donations.models import Subscription
from ovp.apps.organizations.serializers import OrganizationRetrieveSerializer
from django.core.validators import MinValueValidator


class DonateSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    amount = serializers.IntegerField(
        required=True, validators=[
            MinValueValidator(1)])
    organization_id = serializers.IntegerField(required=True)
    anonymous = serializers.BooleanField(required=False)

    def validate(self, data):
        pre_validation = super(DonateSerializer, self).validate(data)
        organization_accepts_donations(data.get("organization_id", None))
        return pre_validation


class TransactionRetrieveSerializer(serializers.ModelSerializer):
    organization = OrganizationRetrieveSerializer()

    class Meta:
        fields = [
            "uuid",
            "organization",
            "amount",
            "status",
            "date_created",
            "date_modified",
            "anonymous"]
        model = Transaction


class UUIDInputSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)


class RefundTransactionSerializer(UUIDInputSerializer):
    pass


class CancelSubscriptionSerializer(UUIDInputSerializer):
    pass


class SubscribeSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    amount = serializers.IntegerField(
        required=True, validators=[
            MinValueValidator(1)])
    interval = serializers.IntegerField(
        required=True, validators=[
            MinValueValidator(1)])
    customer = serializers.CharField(required=True)
    organization_id = serializers.IntegerField(required=True)
    anonymous = serializers.BooleanField(required=False)

    def validate(self, data):
        pre_validation = super(SubscribeSerializer, self).validate(data)
        organization_accepts_donations(data.get("organization_id", None))
        return pre_validation


class SubscriptionRetrieveSerializer(serializers.ModelSerializer):
    organization = OrganizationRetrieveSerializer()

    class Meta:
        fields = [
            "uuid",
            "organization",
            "amount",
            "status",
            "date_created",
            "date_modified",
            "anonymous"]
        model = Subscription
