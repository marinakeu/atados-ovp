from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import response

from ovp.apps.projects.serializers.project import ProjectSearchSerializer

from ovp.apps.channels.viewsets.decorators import ChannelViewSet

from ovp.apps.catalogue.cache import get_catalogue
from ovp.apps.catalogue.cache import fetch_catalogue


RESPONSES_DICT = {
    200: ProjectSearchSerializer(many=True),
    404: 'Not found'
}


@ChannelViewSet
class CatalogueView(generics.GenericAPIView):

    @swagger_auto_schema(responses=RESPONSES_DICT)
    def get(self, request, slug):
        """
        Retrieve a catalogue by slug.
        """
        catalogue = get_catalogue(request.channel, slug, request)
        if not catalogue:
            resp = {"detail": "This catalog does not exist"}
            return response.Response(resp, status=404)

        fetched = fetch_catalogue(
            catalogue,
            serializer=True,
            request=self.request,
            context=self.get_serializer_context(),
            channel=request.channel,
            slug=slug
        )

        return response.Response(fetched)
