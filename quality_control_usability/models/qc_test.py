# Copyright 2022 Daniel Campos - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class QcTest(models.Model):
    _inherit = "qc.test"

    qc_product_tmpl_triggers = fields.One2many(
        comodel_name="qc.trigger.product_template_line",
        inverse_name="test",
        string="Test on products",
    )
