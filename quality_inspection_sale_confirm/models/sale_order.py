# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models

from odoo.addons.quality_control_oca.models.qc_trigger_line import _filter_trigger_lines


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        result = super().action_confirm()
        # At this point sale_stock has launched procurement and created the
        # picking(s) and stock.move(s) for stockable/consumable products.
        self._create_delivery_quality_inspections()
        return result

    def _create_delivery_quality_inspections(self):
        inspection_model = self.env["qc.inspection"].sudo()
        trigger_model = self.env["qc.trigger"].sudo()
        line_models = (
            "qc.trigger.product_category_line",
            "qc.trigger.product_template_line",
            "qc.trigger.product_line",
        )
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda p: p.picking_type_id.code == "outgoing" and p.state != "cancel"
            )
            for picking in pickings:
                triggers = trigger_model.search(
                    [("picking_type_id", "=", picking.picking_type_id.id)]
                )
                for trigger in triggers:
                    partner = (
                        picking.partner_id if trigger.partner_selectable else False
                    )
                    for move in picking.move_lines.filtered(
                        lambda m: m.state != "cancel"
                    ):
                        trigger_lines = set()
                        for model_name in line_models:
                            trigger_lines.update(
                                self.env[model_name]
                                .sudo()
                                .get_trigger_line_for_product(
                                    trigger, move.product_id.sudo(), partner=partner
                                )
                            )
                        for trigger_line in _filter_trigger_lines(trigger_lines):
                            inspection_model._make_inspection(move, trigger_line)
