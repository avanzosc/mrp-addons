from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    bom_id = fields.Many2one("mrp.bom", string="Lista de Materiales")
