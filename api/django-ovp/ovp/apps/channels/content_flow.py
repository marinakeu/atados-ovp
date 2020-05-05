from haystack.query import SQ
from django.db.models import Q


class NoContentFlow(Exception):
    """
    Raised by a content flow class to indicate
    there should not be a content flow for a given model
    """
    pass


class BaseContentFlow():
    def get_filter_searchqueryset_q_obj(self, model_class):
        raise NoContentFlowException

    def get_filter_queryset_q_obj(self, model_class):
        raise NoContentFlowException


class ContentFlowManager():
    flow_dict = {}

    def add_flow(self, flow):
        destination_channel = flow.destination

        if not isinstance(self.flow_dict.get(destination_channel, None), list):
            self.flow_dict[destination_channel] = []

        self.flow_dict[destination_channel].append(flow)

    def filter_searchqueryset(self, destination_channel, queryset):
        if len(queryset.query.models) != 1:
            raise Exception(
                "Channel content flow doesn't implement\
                a solution for multiple models SearchQuerySet"
            )
        model_class = next(iter(queryset.query.models))
        qs = self._filter_qs_or_sqs(
            destination_channel,
            SQ,
            'channel',
            model_class,
            queryset
        )
        return qs

    def filter_queryset(self, destination_channel, queryset, distinct=False):
        model_class = queryset.model
        obj = self._filter_qs_or_sqs(
            destination_channel,
            Q,
            'channel__slug',
            model_class,
            queryset
        )
        if distinct:
            obj = obj.distinct('pk')
        return obj

    def _filter_qs_or_sqs(self, destination_channel, Q_SQ,
                          channel_filter_name, model_class, qs):
        if Q_SQ == Q:
            filter_method = 'get_filter_queryset_q_obj'
        elif Q_SQ == SQ:
            filter_method = 'get_filter_searchqueryset_q_obj'

        q_obj = Q_SQ()
        q_obj.add(Q_SQ(**{channel_filter_name: destination_channel}), Q_SQ.OR)

        if isinstance(self.flow_dict.get(destination_channel, None), list):
            for flow_item in self.flow_dict[destination_channel]:
                content_flow_q_obj = Q_SQ()
                content_flow_q_obj.add(
                    Q_SQ(**{channel_filter_name: flow_item.source}),
                    Q_SQ.AND
                )

                try:
                    content_flow_q_obj.add(
                        getattr(flow_item, filter_method)(model_class),
                        Q_SQ.AND
                    )
                except NoContentFlow:
                    continue

                q_obj.add(content_flow_q_obj, Q_SQ.OR)

        return qs.filter(q_obj)


CFM = ContentFlowManager()
