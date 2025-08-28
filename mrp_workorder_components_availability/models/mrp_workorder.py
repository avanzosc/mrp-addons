from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    mo_components_availability = fields.Char(
        related="production_id.components_availability",
        string="MO Component Status",
        readonly=True,
        help=(
            "Latest component availability status for parent MO. "
            "If green, then the MO's readiness status is ready, "
            "as per BOM configuration."
        ),
    )

    mo_components_availability_state = fields.Selection(
        [("available", "Available"), ("expected", "Expected"), ("late", "Late")],
        related="production_id.components_availability_state",
        readonly=True,
        string="MO Components Availability State",
    )

    mo_reservation_state = fields.Selection(
        [
            ("confirmed", "Waiting"),
            ("assigned", "Ready"),
            ("waiting", "Waiting Another Operation"),
        ],
        string="MO Readiness",
        related="production_id.reservation_state",
        readonly=True,
        help="Manufacturing readiness for parent MO, as per bill of material configuration:\n\
            * Ready: The material is available to start the production.\n\
            * Waiting: The material is not available to start the production.\n",
    )
