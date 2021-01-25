# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    fees_lines = fields.One2many(readonly=False)
    operations = fields.One2many(readonly=False)

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        super(RepairOrder, self).onchange_product_id()
        if not self.partner_id:
            self.pricelist_id = self.env.ref('product.list0')
