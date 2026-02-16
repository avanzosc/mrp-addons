# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class WizReverseInternalPickingFromOF(models.TransientModel):
    _inherit = "wiz.reverse.internal.picking.from.of"

    def button_return(self):
        self.production_id.action_cancel()
        canceled_production = self.env["mrp.production"].browse(self.production_id.id)
        if not self.more_than_one_production and canceled_production.state == "cancel":
            picking_names = ", ".join(
                self.wizard_lines_auto.filtered(
                    lambda x: x.to_cancel and not x.claim_id
                ).mapped("picking_id.name")
            )
            if picking_names:
                error = _(
                    "You must define a claim for these pickings: "
                    "%(picking_names)s,  in order to be able to reverse them."
                ) % {
                    "picking_names": picking_names,
                }
                raise ValidationError(error)
            for line in self.wizard_lines_auto.filtered(lambda x: x.to_cancel):
                if (
                    not line.picking_id.claim_id
                    or line.picking_id.claim_id.id != line.claim_id.id
                ):
                    line.picking_id.claim_id = line.claim_id.id
        return super().button_return()


class WizReverseInternalPickingFromOFLineAuto(models.TransientModel):
    _inherit = "wiz.reverse.internal.picking.from.of.line.auto"

    claim_id = fields.Many2one(string="Claim", comodel_name="crm.claim")
