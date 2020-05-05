from ovp.apps.faq.models.category import FaqCategory
from ovp.apps.channels.serializers import ChannelRelationshipSerializer


class CategoryFaqRetrieveSerializer(ChannelRelationshipSerializer):
    class Meta:
        model = FaqCategory
        fields = ['id', 'name']
