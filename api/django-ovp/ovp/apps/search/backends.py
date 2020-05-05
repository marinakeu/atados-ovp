from django.conf import settings

from ovp.apps.core.helpers import get_settings

from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
from haystack.backends.elasticsearch_backend import ElasticsearchSearchEngine


class ConfigurableElasticBackend(ElasticsearchSearchBackend):

    DEFAULT_ANALYZER = "snowball"

    def __init__(self, connection_alias, **connection_options):
        super().__init__(connection_alias, **connection_options)

        user_settings = get_settings('ELASTICSEARCH_INDEX_SETTINGS')
        if user_settings:
            setattr(self, 'DEFAULT_SETTINGS', user_settings)

    def build_schema(self, fields):
        content_field_name, mapping = super().build_schema(fields)

        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if field_mapping['type'] == 'string' and field_class.indexed:
                if not hasattr(field_class, 'facet_for') and not \
                        field_class.field_type in('ngram', 'edge_ngram'):
                    field_mapping['analyzer'] = self.DEFAULT_ANALYZER
            mapping.update({field_class.index_fieldname: field_mapping})
        return (content_field_name, mapping)


class ConfigurableElasticSearchEngine(ElasticsearchSearchEngine):
    backend = ConfigurableElasticBackend
