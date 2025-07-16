# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    photo1 = fields.Binary(attachment=True)
    photo2 = fields.Binary(attachment=True)
    photo3 = fields.Binary(attachment=True)
    photo4 = fields.Binary(attachment=True)
