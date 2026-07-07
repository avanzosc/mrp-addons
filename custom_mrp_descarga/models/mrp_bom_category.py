from odoo import fields, models


class MrpBomCategory(models.Model):

    _inherit = "mrp.bom.category"

    is_quartering = fields.Boolean(string="Quartering", default=False, store=True)
    bring_components_on_confirm = fields.Boolean(
        string="Bring Components on Confirm",
        default=False,
        help="When confirming a production order with this category, "
        "automatically create input lines for all storable BOM components "
        "without requiring lot reservation.",
    )
