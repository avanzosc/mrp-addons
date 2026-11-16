# (c) José A. Ballate - Guadaltech
# (c) Ignacio Ales López - Guadaltech
# (c) 2024 Alfredo de la Fuente - Avanzosc
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    production_multiple = fields.Float(default=0, required=False)
