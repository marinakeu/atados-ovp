import csv
from datetime import datetime

from django.http import HttpResponse


class Response(object):
    """
    class created to assist responses with HttpResponse objects.

    Converts queries to csv documents and adds
    appropriate headers to the HttpResponse.
    """

    def __init__(self, rows, filename=None, sheet_name=None):
        self.rows = rows
        self.filename = filename
        self.sheet_name = sheet_name
        return self._render_csv()

    def _render_csv(self):
        if self.filename is None:
            now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            self.filename = "data-export-{}.csv".format(now)
        response = HttpResponse(content_type='text/csv')
        content_disposition = 'attachment; filename="{}"'.format(self.filename)
        response['Content-Disposition'] = content_disposition

        csv_writer = csv.writer(response)
        for row in self.rows:
            csv_writer.writerow(row)

        return response
