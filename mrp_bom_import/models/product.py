# Copyright (c) 2019 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    map_number = fields.Char(string="Map Number")


class ProductCategory(models.Model):
    _inherit = "product.category"

    supplier_id = fields.Many2one(comodel_name="res.partner", string="Supplier")
