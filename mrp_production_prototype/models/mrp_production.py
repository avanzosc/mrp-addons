# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_prototype = fields.Boolean(string="Is Prototype?", default=False, copy=False)
    prototype_validation_date = fields.Date(copy=False)
    prototype_order_id = fields.Many2one(
        string="Prototype Manufacturing Order",
        comodel_name="mrp.production",
        copy=False,
    )
    prototype_order_state = fields.Selection(
        string="Prototype Order State",
        related="prototype_order_id.state",
        store=True,
        copy=False,
    )
    parent_prototype_validation_date = fields.Date(
        string="Prototype Validation Date",
        store=True,
        copy=False,
        related="prototype_order_id.prototype_validation_date",
    )

    @api.onchange("is_prototype")
    def _onchange_is_prototype(self):
        for production in self:
            if production.is_prototype:
                production.prototype_order_id = False
            else:
                production.prototype_validation_date = False
