# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from base64 import b64decode, b64encode
from io import BytesIO
from logging import getLogger
from reportlab.lib.pagesizes import A4 as A4

logger = getLogger(__name__)

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass
try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
except ImportError:
    logger.debug("Can not import PyPDF2")


def print_report(records, qweb_name):
    if not records:
        return
    pdf = PdfFileWriter()
    width, height = A4
    for record in records:
        content, content_type = records.env.ref(qweb_name).render_qweb_pdf(
            res_ids=record.id)

        content_pdf = PdfFileReader(BytesIO(content))
        if record._name == "mrp.workorder":
            worksheet = record.worksheet
        elif record._name == "mrp.workorder.line":
            worksheet = record.finished_workorder_id.worksheet
        elif record._name == "mrp.workorder.nest.line":
            worksheet = record.workorder_id.worksheet
        else:
            break
        pdf_worksheet = PdfFileReader(
            BytesIO(b64decode(worksheet)),
            strict=False)

        for page in pdf_worksheet.pages:
            new_page = pdf.addBlankPage(width, height)
            new_page.mergePage(content_pdf.getPage(0))
            page.scaleBy(0.95)
            new_page.mergePage(page)

    pdf_content = BytesIO()
    pdf.write(pdf_content)
    pdf_data = pdf_content.getvalue()
    pdf_encoded = b64encode(pdf_data)
    return pdf_encoded


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def print_report(self):
        records = self.filtered(lambda r: r.worksheet)
        return print_report(
            records,
            "mrp_workorder_data_worksheet_header.mrp_workorder_worksheet_report")

    def get_worksheets(self):
        pdf = self.print_report()
        if not pdf or not self.env.context.get("print", False):
            return self.filtered("worksheet").mapped("worksheet")
        return pdf

    def show_worksheets(self):
        self.ensure_one()
        if self.env.context.get("print_nest", False):
            worksheets = self.mapped(
                "finished_workorder_line_ids").get_worksheets()
        else:
            worksheets = self.get_worksheets()
        if not worksheets:
            return
        wizard = self.env["binary.container"].create({
            "binary_field": (
                worksheets[0] if isinstance(worksheets, list) else worksheets),
        })
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update({
            "name": _("Worksheets"),
            "res_id": wizard.id,
        })
        return action_dict
