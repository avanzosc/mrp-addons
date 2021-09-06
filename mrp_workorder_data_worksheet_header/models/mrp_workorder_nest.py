# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MrpWorkorderNest(models.Model):
    _inherit = "mrp.workorder.nest"

    def show_worksheets(self):
        self.ensure_one()
        pdf = self.mapped("nested_line_ids.workorder_id."
                          "finished_workorder_line_ids").print_report()
        if not pdf and self.worksheets:
            return super().show_worksheets()
        wizard = self.env["binary.container"].create({
            "binary_field": pdf,
        })
        view_ref = self.env["ir.model.data"].get_object_reference(
            "mrp_workorder_grouping_by_material",
            "binary_container_view")
        view_id = view_ref and view_ref[1] or False,
        return {
            "name": "Worksheet",
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
