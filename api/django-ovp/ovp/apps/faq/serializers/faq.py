from ovp.apps.faq.models.faq import Faq
from ovp.apps.faq.serializers.category import CategoryFaqRetrieveSerializer

from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class FaqRetrieveSerializer(ChannelRelationshipSerializer):
    category = CategoryFaqRetrieveSerializer()

    class Meta:
        model = Faq
        fields = ['id', 'question', 'answer', 'language', 'category']
