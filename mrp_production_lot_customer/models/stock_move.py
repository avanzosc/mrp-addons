# Copyright 2022 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        self.ensure_one()
        customer = False
        if (
            self.raw_material_production_id
            and self.raw_material_production_id.lot_customer_id
        ):
            customer = self.raw_material_production_id.lot_customer_id
        if not customer:
            result = super(StockMove, self)._update_reserved_quantity(
                need,
                available_quantity,
                location_id,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )
        else:
            result = super(
                StockMove, self.with_context(customer=customer)
            )._update_reserved_quantity(
                need,
                available_quantity,
                location_id,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )
        return result
