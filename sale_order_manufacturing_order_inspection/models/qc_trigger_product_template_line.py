# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class QcTriggerProductTemplateLine(models.Model):
    _inherit = "qc.trigger.product_template_line"

    service_product_id = fields.Many2one(
        string="Service Product",
        comodel_name="product.product",
        domain="[('type', '=', 'service')]",
    )
