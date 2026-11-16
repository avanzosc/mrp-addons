# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

KILLING_COST_DIGITS = (16, 3)


class KillingCost(models.Model):
    _name = "killing.cost"
    _description = "Workcenter Cost"

    workcenter_id = fields.Many2one(comodel_name="mrp.workcenter")
    january = fields.Float(digits=KILLING_COST_DIGITS)
    february = fields.Float(digits=KILLING_COST_DIGITS)
    march = fields.Float(digits=KILLING_COST_DIGITS)
    april = fields.Float(digits=KILLING_COST_DIGITS)
    may = fields.Float(digits=KILLING_COST_DIGITS)
    june = fields.Float(digits=KILLING_COST_DIGITS)
    july = fields.Float(digits=KILLING_COST_DIGITS)
    august = fields.Float(digits=KILLING_COST_DIGITS)
    september = fields.Float(digits=KILLING_COST_DIGITS)
    october = fields.Float(digits=KILLING_COST_DIGITS)
    november = fields.Float(digits=KILLING_COST_DIGITS)
    december = fields.Float(digits=KILLING_COST_DIGITS)
