# Copyright 2026 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class RepairOrder(models.Model):
    _inherit = "repair.order"

    def _compute_sale_order(self):
        for rec in self:
            rec.sale_order_ids = (
                rec.mapped("operations.sale_line_id.order_id")
                | rec.mapped("fees_lines.sale_line_id.order_id")
            ).ids
            rec.sale_order_count = len(rec.sale_order_ids)

    def action_validate(self):
        if self.filtered(
            lambda x: x.create_sale_order and not x.operations and x.fees_lines
        ):
            self.ensure_one()
            if self.filtered(
                lambda repair: any(op.product_uom_qty < 0 for op in repair.operations)
            ):
                raise UserError(_("You can not enter negative quantities."))
            self._check_product_tracking()
            if self.product_id.type == "consu":
                return self.action_repair_confirm()
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            available_qty_owner = self.env["stock.quant"]._get_available_quantity(
                self.product_id,
                self.location_id,
                self.lot_id,
                owner_id=self.partner_id,
                strict=True,
            )
            available_qty_noown = self.env["stock.quant"]._get_available_quantity(
                self.product_id, self.location_id, self.lot_id, strict=True
            )
            repair_qty = self.product_uom._compute_quantity(
                self.product_qty, self.product_id.uom_id
            )
            for available_qty in [available_qty_owner, available_qty_noown]:
                if (
                    float_compare(available_qty, repair_qty, precision_digits=precision)
                    >= 0
                ):
                    return self.action_repair_confirm()
            else:
                return {
                    "name": self.product_id.display_name
                    + _(": Insufficient Quantity To Repair"),
                    "view_mode": "form",
                    "res_model": "stock.warn.insufficient.qty.repair",
                    "view_id": self.env.ref(
                        "repair.stock_warn_insufficient_qty_repair_form_view"
                    ).id,
                    "type": "ir.actions.act_window",
                    "context": {
                        "default_product_id": self.product_id.id,
                        "default_location_id": self.location_id.id,
                        "default_repair_id": self.id,
                        "default_quantity": repair_qty,
                        "default_product_uom_name": self.product_id.uom_name,
                    },
                    "target": "new",
                }
        else:
            return super().action_validate()

    def action_create_sale_order(self):
        result = super().action_create_sale_order()
        order_model = self.env["sale.order"].sudo()
        order_line_model = self.env["sale.order.line"].sudo()
        sale_order = order_model.browse(result.get("res_id"))
        for rec in self.filtered(
            lambda x: not x.sale_order_ids and x.create_sale_order
        ):
            for line in rec.fees_lines:
                sale_order_line = order_line_model.create(
                    line._get_sale_line_data(sale_order)
                )
                line.sale_line_id = sale_order_line.id
        return result
