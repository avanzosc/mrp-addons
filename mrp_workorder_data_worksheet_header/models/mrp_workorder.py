# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from base64 import b64decode, b64encode
from io import BytesIO
from logging import getLogger

logger = getLogger(__name__)

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass
try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
except ImportError:
    logger.debug("Can not import PyPDF2")


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    worksheet_header = fields.Binary(string='PDF', help="Upload your PDF "
                                                        "file.")

    def print_report(self):
        if not self.worksheet:
            return
        content, content_type = self.env.ref(
            'mrp_workorder_data_worksheet_header.'
            'mrp_workorder_data_worksheet_header_report'
        ).render_qweb_pdf(self.id)

        content_pdf = PdfFileReader(BytesIO(content))
        pdf_worksheet = PdfFileReader(BytesIO(b64decode(self.worksheet)),
                                      strict=False)

        pdf = PdfFileWriter()
        for page in pdf_worksheet.pages:
            new_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight(),
            )
            new_page.mergePage(content_pdf.getPage(0))
            page.scaleBy(0.95)
            new_page.mergePage(page)

        pdf_content = BytesIO()
        pdf.write(pdf_content)
        pdf_data = pdf_content.getvalue()
        pdf_encoded = b64encode(pdf_data)
        self.worksheet_header = pdf_encoded
        return pdf_encoded

    def show_worksheet(self):
        pdf = self.print_report()
        if not pdf:
            return
        wizard = self.env['binary.container'].create(
            {'binary_field': pdf})
        view_ref = self.env['ir.model.data'].get_object_reference(
            'mrp_workorder_data_worksheet_header',
            'binary_container_view')
        view_id = view_ref and view_ref[1] or False,
        return {
            'name': 'Worksheet',
            'domain': [],
            'res_model': 'binary.container',
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'context': {},
            'target': 'new',
        }
