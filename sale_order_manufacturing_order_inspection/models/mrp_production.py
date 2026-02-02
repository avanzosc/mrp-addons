# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models

from odoo.addons.quality_control_oca.models.qc_trigger_line import _filter_trigger_lines


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    service_product_id = fields.Many2one(
        string="Service Product",
        comodel_name="product.product",
        domain="[('type', '=', 'service')]",
    )

    def action_create_inspection_from_of(self):
        qc_trigger_mrp = self.env["qc.trigger"].get_manufacturing_trigger()
        if not qc_trigger_mrp:
            return
        for production in self:
            qc_triggers = (
                production.product_id.qc_triggers
                or production.product_id.product_tmpl_id.qc_triggers
            )
            if production.service_product_id:
                qc_trigger = qc_triggers.filtered(
                    lambda x: x.trigger == qc_trigger_mrp
                    and x.service_product_id == production.service_product_id
                )
            else:
                qc_trigger = qc_triggers.filtered(
                    lambda x: x.trigger == qc_trigger_mrp and not x.service_product_id
                )
            if qc_trigger:
                for move in production.move_finished_ids:
                    trigger_lines = set()
                    for model in [
                        "qc.trigger.product_category_line",
                        "qc.trigger.product_template_line",
                        "qc.trigger.product_line",
                    ]:
                        trigger_lines = trigger_lines.union(
                            self.env[model].get_trigger_line_for_product(
                                qc_trigger.trigger, move.product_id
                            )
                        )
                    trigger_lines = {
                        trigger_line
                        for trigger_line in trigger_lines
                        if not (
                            (
                                trigger_line._name
                                in (
                                    "qc.trigger.product_line",
                                    "qc.trigger.product_template_line",
                                )
                                and production.service_product_id
                                and (
                                    not trigger_line.service_product_id
                                    or trigger_line.service_product_id
                                    != production.service_product_id
                                )
                            )
                            or (
                                not production.service_product_id
                                and trigger_line.service_product_id
                            )
                        )
                    }
                    for trigger_line in _filter_trigger_lines(trigger_lines):
                        for qc_test_label in trigger_line.test.qc_test_label_ids:
                            inspection = (
                                self.env["qc.inspection"]
                                .with_context(
                                    service_product_id=production.service_product_id.id
                                )
                                ._make_inspection(move, trigger_line)
                            )
                            name = "%(display_name)s - %(label_name)s" % {
                                "display_name": inspection.name,
                                "label_name": qc_test_label.name,
                            }
                            inspection.name = name
