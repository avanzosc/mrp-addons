from odoo import fields, models


class MrpBomCategory(models.Model):

    _inherit = "mrp.bom.category"

    is_quartering = fields.Boolean(string="Quartering", default=False, store=True)
