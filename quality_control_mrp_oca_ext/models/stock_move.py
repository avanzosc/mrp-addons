# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    qc_inspection_type_id = fields.Many2one(
        string="Inspection type",
        comodel_name="qc.inspection.type",
        related="product_id.qc_inspection_type_id",
        readonly=True,
        copy=False,
        store=True,
    )
