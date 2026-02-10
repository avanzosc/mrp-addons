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

    def action_confirm(self):
        self.sale_id._put_service_product_in_production(self)
        res = super().action_confirm()
        for production in self:
            production.action_create_inspection_from_of()
        return res

    def action_create_inspection_from_of(self):
        qc_trigger_mrp = self.env["qc.trigger"].get_manufacturing_trigger()
        if not qc_trigger_mrp:
            return
        for production in self:
            qc_triggers = (
                production.product_id.qc_triggers
                or production.product_id.product_tmpl_id.qc_triggers
            )
            qc_trigger = qc_triggers.filtered(
                lambda x: x.trigger == qc_trigger_mrp
                and (
                    not x.service_product_id
                    or x.service_product_id == production.service_product_id
                )
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
                        if not trigger_line.service_product_id
                        or (
                            production.service_product_id
                            and trigger_line.service_product_id
                            == production.service_product_id
                        )
                    }
                    for trigger_line in _filter_trigger_lines(trigger_lines):
                        test_labels = trigger_line.test.qc_test_label_ids
                        Inspection = self.env["qc.inspection"].with_context(
                            service_product_id=production.service_product_id.id
                            if production.service_product_id
                            else False
                        )
                        if not test_labels:
                            Inspection._make_inspection(move, trigger_line)
                            continue
                        existing_inspections = self.env["qc.inspection"].search(
                            [
                                ("production_id", "=", production.id),
                                ("object_id", "=", "stock.move,%d" % move.id),
                                ("test", "=", trigger_line.test.id),
                            ]
                        )
                        existing_label_ids = set()
                        for insp in existing_inspections:
                            for label in test_labels:
                                if label.name in (insp.name or ""):
                                    existing_label_ids.add(label.id)
                        labels_missing = [
                            label
                            for label in test_labels
                            if label.id not in existing_label_ids
                        ]
                        if labels_missing:
                            for label in labels_missing:
                                inspection = Inspection._make_inspection(
                                    move, trigger_line
                                )
                                inspection.name = "%s - %s" % (
                                    inspection.name,
                                    label.name,
                                )
                        else:
                            Inspection._make_inspection(move, trigger_line)
