# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class QcTest(models.Model):
    _inherit = "qc.test"

    test_for_manufacturing_orders = fields.Boolean(
        string="Test for manufacturing orders", default=False
    )
    product_ids = fields.Many2many(string="Products", comodel_name="product.product")
    product_category_ids = fields.Many2many(
        string="Product categories", comodel_name="product.category"
    )


class QcTestQuestion(models.Model):
    _inherit = "qc.test.question"

    component = fields.Char()
