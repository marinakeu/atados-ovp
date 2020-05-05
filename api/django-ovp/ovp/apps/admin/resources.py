import tablib
from import_export import resources
from django.db.models.query import QuerySet
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE


class CleanModelResource(resources.ModelResource):
    def export_field(self, field, obj):
        v = super(CleanModelResource, self).export_field(field, obj)
        if isinstance(v, str):
            v = ILLEGAL_CHARACTERS_RE.sub('', v)
        return v

    def export(self, queryset=None, *args, **kwargs):
        """
        Exports a resource. We override ModelResource.export to allow
        self.before_export to return a queryset.
        We also reenable queryset caching which is disabled by import_export
        """
        if queryset is None:
            queryset = self.get_queryset()

        be = self.before_export(queryset, *args, **kwargs)
        queryset = be if be else queryset

        headers = self.get_export_headers()
        data = tablib.Dataset(headers=headers)

        iterable = queryset
        for obj in iterable:
            data.append(self.export_resource(obj))

        self.after_export(queryset, data, *args, **kwargs)

        return data
