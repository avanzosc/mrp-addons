# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    extended_quality_control_ids = fields.One2many(
        string="Production control",
        comodel_name="extended.quality.control",
        related="production_id.extended_quality_control_ids",
    )
    operator_id = fields.Many2one(
        string="Operator",
        comodel_name="res.users",
        copy=False,
    )
    software = fields.Char()
    print_production_information = fields.Boolean(
        string="Print production data",
        default=False,
    )

    def _prepare_inspection_line(self, test, line, fill=None):
        data = super()._prepare_inspection_line(test, line, fill=fill)
        data["component"] = line.component
        return data

    def _make_inspection(self, object_ref, trigger_line):
        found = False
        if object_ref and object_ref._name != "stock.move":
            found = True
        if object_ref and object_ref._name == "stock.move":
            if (
                trigger_line.test
                and not trigger_line.test.test_for_manufacturing_orders
            ):
                found = True
            if trigger_line.test and trigger_line.test.test_for_manufacturing_orders:
                if (
                    not trigger_line.test.product_category_ids
                    or not object_ref.production_id
                    or not object_ref.product_id
                ):
                    found = True
                if (
                    trigger_line.test.product_category_ids
                    and object_ref.production_id
                    and object_ref.product_id
                ):
                    if (
                        object_ref.product_id.categ_id.id
                        in trigger_line.test.product_category_ids.ids
                    ):
                        found = True
                    else:
                        if (
                            object_ref.product_id.categ_id.parent_id
                            and object_ref.product_id.categ_id.parent_id.id
                            in trigger_line.test.product_category_ids.ids
                        ):
                            found = True
        if found:
            inspection = super()._make_inspection(object_ref, trigger_line)
        else:
            inspection = self.env["qc.inspection"]
        return inspection


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    component = fields.Char()
