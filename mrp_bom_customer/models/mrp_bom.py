# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.models import expression


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        copy=False,
    )

    @api.model
    def _bom_find_domain(
        self, products, picking_type=None, company_id=False, bom_type=False
    ):
        domain = super()._bom_find_domain(
            products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        partner_id = self.env.context.get("default_partner_id", False)
        partner_domain = [("customer_id", "=", False)]
        if partner_id:
            partner_domain = expression.OR(
                [partner_domain, [("customer_id", "=", partner_id)]]
            )
        domain = expression.AND([domain, partner_domain])
        return domain
