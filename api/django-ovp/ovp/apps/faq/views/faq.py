from ovp.apps.faq.models.faq import Faq
from ovp.apps.faq.serializers.faq import FaqRetrieveSerializer

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import response


@ChannelViewSet
class FaqResourceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Faq.objects.all()

    def list(self, request):
        """
        Retrieve list of frequently asked questions.
        """
        category = request.query_params.get('category', None)
        language = request.query_params.get('language', None)
        queryset = self.get_queryset()

        queryset = queryset.filter(category=category) if category else queryset
        queryset = queryset.filter(language=language) if language else queryset

        serializer = FaqRetrieveSerializer(queryset, many=True)

        return response.Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'list':
            return FaqRetrieveSerializer
