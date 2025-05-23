# Copyright 2024 Alfredo de la Fuente - Avanzosc S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    iso_quality_control = fields.Char(string="Certification ISO for quality control")
