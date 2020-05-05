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
class OrganizationDonationViewSet(viewsets.GenericViewSet):
    pass
