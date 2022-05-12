from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    employee_id = fields.Many2one("hr.employee", string="Responsible Employee")