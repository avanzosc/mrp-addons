# Copyright 2023 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_emptying_location(self):
        self.ensure_one()
        if self.location_src_id:
            self.move_line_ids.unlink()
            for quant in self.location_src_id.quant_ids.filtered(
                lambda c: c.product_id != self.product_id and c.available_quantity > 0
            ):
                self.env["stock.move"].create(
                    {
                        "product_id": quant.product_id.id,
                        "name": quant.product_id.name,
                        "product_uom": quant.product_id.uom_id.id,
                        "product_uom_qty": quant.available_quantity,
                        "location_id": quant.location_id.id,
                        "location_dest_id": self.production_location_id.id,
                        "company_id": self.company_id.id,
                        "raw_material_production_id": self.id,
                        "move_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": quant.product_id.id,
                                    "product_uom_id": quant.product_id.uom_id.id,
                                    "qty_done": quant.available_quantity,
                                    "location_id": quant.location_id.id,
                                    "location_dest_id": self.production_location_id.id,
                                    "standard_price": quant.product_id.standard_price,
                                    "company_id": self.company_id.id,
                                    "amount": quant.available_quantity
                                    * quant.product_id.standard_price,
                                    "lot_id": quant.lot_id.id,
                                    "production_id": self.id,
                                },
                            )
                        ],
                    }
                )
            self.action_confirm()
            self.product_qty = sum(self.move_line_ids.mapped("qty_done"))
            self.qty_producing = sum(self.move_line_ids.mapped("qty_done"))
