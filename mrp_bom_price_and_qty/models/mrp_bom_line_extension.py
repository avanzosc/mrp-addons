from odoo import models, fields, api
import requests

class MrpBomLineExtension(models.Model):
    _inherit = 'mrp.bom.line'

    prod_price = fields.Float(string='Product Price', compute='_compute_prod_price')

    @api.depends('product_id')
    def _compute_prod_price(self):
        for line in self:
            if line.product_id:
                response = requests.get(f'http://example.com/api/product_price/{line.product_id.id}')
                if response.status_code == 200:
                    price = response.json().get('price', 0.0)
                    line.prod_price = round(price, 4)
