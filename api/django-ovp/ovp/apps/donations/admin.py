from django import forms

from ovp.apps.channels.admin import admin_site
from ovp.apps.channels.admin import ChannelModelAdmin
from ovp.apps.donations.models import Transaction
from ovp.apps.donations.models import Subscription


class TransactionAdmin(ChannelModelAdmin):
    fields = [
        'uuid',
        'user',
        'organization',
        'amount',
        'status',
        'message',
        'backend_transaction_id',
        'backend_transaction_number',
        'date_created',
        'date_modified'
    ]

    list_display = [
        'uuid',
        'organization',
        'amount',
        'status',
        'user',
        'backend_transaction_id',
        'backend_transaction_number'
    ]

    list_filter = []

    list_editable = []

    search_fields = [
        'uuid',
        'user__name',
        'organization__name',
        'status',
        'backend_transaction_id',
        'backend_transaction_number']

    readonly_fields = [
        'uuid',
        'user',
        'organization',
        'amount',
        'status',
        'message',
        'backend_transaction_id',
        'backend_transaction_number',
        'date_created',
        'date_modified'
    ]


class SubscriptionAdmin(ChannelModelAdmin):
    fields = [
        'uuid',
        'user',
        'organization',
        'amount',
        'status',
        'backend_subscription_id',
        'backend_plan_id',
        'date_created',
        'date_modified'
    ]

    list_display = [
        'uuid',
        'organization',
        'amount',
        'status',
        'user',
        'backend_subscription_id',
        'backend_plan_id'
    ]

    list_filter = []

    list_editable = []

    search_fields = [
        'uuid',
        'user__name',
        'organization__name',
        'status',
        'backend_transaction_id',
        'backend_transaction_number']

    readonly_fields = [
        'uuid',
        'user',
        'organization',
        'amount',
        'status',
        'backend_subscription_id',
        'backend_plan_id',
        'date_created',
        'date_modified'
    ]


admin_site.register(Subscription, SubscriptionAdmin)
admin_site.register(Transaction, TransactionAdmin)
