from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    internal_picking_ids = fields.One2many(
        "stock.picking",
        "mrp_production_id",
        string="Internal Pickings",
    )

    def action_open_internal_pickings(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Internal Pickings",
            "view_mode": "tree,form",
            "res_model": "stock.picking",
            "domain": [("id", "in", self.internal_picking_ids.ids)],
        }
