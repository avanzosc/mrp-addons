# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class WizReverseInternalPickingFromOF(models.TransientModel):
    _name = "wiz.reverse.internal.picking.from.of"
    _description = "Wizard For Reverse Intenal Picking From OF"

    production_id = fields.Many2one(
        string="Production To Cancel", comodel_name="mrp.production"
    )
    more_than_one_production = fields.Boolean(string="more than one production")
    other_productions = fields.Many2many(
        string="Related productions", comodel_name="mrp.production"
    )
    wizard_lines_auto = fields.One2many(
        string="Lines",
        comodel_name="wiz.reverse.internal.picking.from.of.line.auto",
        inverse_name="wizard_id",
    )
    wizard_lines_manual = fields.One2many(
        string="Lines",
        comodel_name="wiz.reverse.internal.picking.from.of.line.manual",
        inverse_name="wizard_id",
    )

    def button_return(self):
        self.production_id.action_cancel()
        canceled_production = self.env["mrp.production"].browse(self.production_id.id)
        if not self.more_than_one_production and canceled_production.state == "cancel":
            for line in self.wizard_lines_auto.filtered(lambda x: x.to_cancel):
                return_picking_obj = self.env["stock.return.picking"].with_context(
                    active_id=line.picking_id.id,
                    active_ids=[line.picking_id.id],
                    active_model="stock.picking",
                )
                default_vals = return_picking_obj.default_get(
                    return_picking_obj._fields.keys()
                )
                new_wizard = return_picking_obj.new(default_vals)
                for comp_onchange in new_wizard._onchange_methods["picking_id"]:
                    comp_onchange(new_wizard)
                values = new_wizard._convert_to_write(new_wizard._cache)
                wizard = return_picking_obj.create(values)
                wizard.create_returns()


class WizReverseInternalPickingFromOFLineAuto(models.TransientModel):
    _name = "wiz.reverse.internal.picking.from.of.line.auto"
    _description = "Wizard For Reverse Intenal Picking From OF Line"

    wizard_id = fields.Many2one(
        string="Wizard", comodel_name="wiz.reverse.internal.picking.from.of"
    )
    to_cancel = fields.Boolean(default=True)
    picking_id = fields.Many2one(string="Picking", comodel_name="stock.picking")


class WizReverseInternalPickingFromOFLineManual(models.TransientModel):
    _name = "wiz.reverse.internal.picking.from.of.line.manual"
    _description = "Wizard For Reverse Intenal Picking From OF Line"

    wizard_id = fields.Many2one(
        string="Wizard", comodel_name="wiz.reverse.internal.picking.from.of"
    )
    picking_id = fields.Many2one(string="Picking", comodel_name="stock.picking")
