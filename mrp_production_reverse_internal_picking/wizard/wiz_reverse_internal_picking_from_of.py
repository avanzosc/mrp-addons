# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class WizReverseInternalPickingFromOF(models.TransientModel):
    _name = "wiz.reverse.internal.picking.from.of"
    _description = "Wizard For Reverse Intenal Picking From OF"

    picking_id = fields.Many2one(
        string="Picking To Be Returned", comodel_name="stock.picking"
    )

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        result["picking_id"] = self.env.context.get("default_picking_id")
        return result

    def button_return(self):
        return_picking_obj = self.env["stock.return.picking"].with_context(
            active_id=self.picking_id.id,
            active_ids=[self.picking_id.id],
            active_model="stock.picking",
        )
        default_vals = return_picking_obj.default_get(return_picking_obj._fields.keys())
        new_wizard = return_picking_obj.new(default_vals)
        for comp_onchange in new_wizard._onchange_methods["picking_id"]:
            comp_onchange(new_wizard)
        values = new_wizard._convert_to_write(new_wizard._cache)
        wizard = return_picking_obj.create(values)
        wizard.create_returns()
