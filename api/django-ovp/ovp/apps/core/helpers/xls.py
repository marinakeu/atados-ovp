from io import BytesIO
from datetime import datetime

from pyexcel_xls import save_data

from django.http import HttpResponse


class Response(object):
    """
    class created to assist responses with HttpResponse objects.

    Converts queries to xls documents and adds
    appropriate headers to the HttpResponse.
    """

    def __init__(self, rows, filename=None, sheet_name="root"):
        self.rows = rows
        self.filename = filename
        self.sheet_name = sheet_name

    def _render_xls(self):
        if self.filename is None:
            now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            self.filename = "data-export-{}.xls".format(now)

        xls_buffer = BytesIO()
        save_data(xls_buffer, {str(self.sheet_name): self.rows})

        response = HttpResponse(
            xls_buffer.getvalue(),
            content_type='application/vnd.ms-excel'
        )
        content_disposition = 'attachment; filename="{}"'.format(self.filename)
        response['Content-Disposition'] = content_disposition

        return response
