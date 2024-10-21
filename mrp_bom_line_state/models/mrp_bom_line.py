# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class MrpBomLine(models.Model):

    _inherit = "mrp.bom.line"

    state = fields.Selection(
        selection=[("draft", "Draft"), ("active", "Active"),
                   ("historical", "Historical")], string="State",
        store=True, readonly=True, copy=False,
        related="bom_id.state")
