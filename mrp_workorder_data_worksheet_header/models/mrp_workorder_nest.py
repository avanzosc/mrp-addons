# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import tempfile

from PyPDF2 import PdfFileMerger

from odoo import api, models

class MrpWorkorderNest(models.Model):
    _inherit = "mrp.workorder.nest"

    def _get_worksheets(self):
        worksheets = []
        for workorder in self.nested_line_ids.mapped('workorder_id'):
            workorder.print_report()
            if workorder.worksheet_header:
                worksheets.append(workorder.worksheet_header)
        return worksheets

    def show_worksheets(self):
        for nest in self:
            worksheets = self._get_worksheets()
            merger = PdfFileMerger(strict=False)
            for worksheet in worksheets:
                temp = tempfile.NamedTemporaryFile(suffix='.pdf')
                with open(temp.name, 'wb') as temp_pdf:
                    pdf = base64.b64decode(worksheet)
                    temp_pdf.write(pdf)
                merger.append(temp.name, import_bookmarks=False)
            temp = tempfile.NamedTemporaryFile(suffix='.pdf')
            merger.write(temp.name)
            merger.close()

            with open(temp.name, 'rb') as merged_pdf:
                content_merged_pdf = merged_pdf.read()
            nest.worksheets = base64.b64encode(content_merged_pdf)
            wizard = self.env['binary.container'].create(
                {'binary_field': nest.worksheets})
            view_ref = self.env['ir.model.data'].get_object_reference(
                'mrp_workorder_grouping_by_material',
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