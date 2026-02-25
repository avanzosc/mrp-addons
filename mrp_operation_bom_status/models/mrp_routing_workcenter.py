from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    mrp_operation_bom_status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("historical", "Historical"),
        ],
        string="BOM status",
        compute="_compute_mrp_operation_bom_status",
        store=True,
        readonly=True,
    )

    @api.depends("bom_id", "bom_id.state")
    def _compute_mrp_operation_bom_status(self):
        for rec in self:
            rec.mrp_operation_bom_status = rec.bom_id.state or False
