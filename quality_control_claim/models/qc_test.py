# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class QcTest(models.Model):
    _inherit = "qc.test"

    automatic_claims = fields.Boolean(
        default=False,
        help="If you want to create one claim when the quality test status is"
        " 'Quality failed'.",
    )
    automatic_claims_by_line = fields.Boolean(
        default=False,
        help="If you want to create one claim per quality test line, when the"
        " quality test line status is 'No ok'.",
    )
