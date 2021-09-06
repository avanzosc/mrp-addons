# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def show_worksheet(self):
        self.ensure_one()
        pdf = self.mapped("finished_workorder_line_ids").print_report()
        if not pdf:
            return
        wizard = self.env["binary.container"].create({
            "binary_field": pdf,
        })
        view_ref = self.env["ir.model.data"].get_object_reference(
            "mrp_workorder_data_worksheet_header",
            "binary_container_view")
        view_id = view_ref and view_ref[1] or False,
        return {
            "name": _("Worksheet"),
            "domain": [],
            "res_model": "binary.container",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "view_id": view_id,
            "context": {},
            "target": "new",
        }
