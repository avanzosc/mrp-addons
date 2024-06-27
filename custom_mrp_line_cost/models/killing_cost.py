# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class KillingCost(models.Model):
    _name = "killing.cost"
    _description = "Workcenter Cost"

    workcenter_id = fields.Many2one(
        string="Workcenter",
        comodel_name="mrp.workcenter",
    )
    january = fields.Float(
        string="January",
        digits="Killing Cost Decimal Precision",
    )
    february = fields.Float(
        string="February",
        digits="Killing Cost Decimal Precision",
    )
    march = fields.Float(
        string="March",
        digits="Killing Cost Decimal Precision",
    )
    april = fields.Float(
        string="April",
        digits="Killing Cost Decimal Precision",
    )
    may = fields.Float(
        string="May",
        digits="Killing Cost Decimal Precision",
    )
    june = fields.Float(
        string="June",
        digits="Killing Cost Decimal Precision",
    )
    july = fields.Float(
        string="July",
        digits="Killing Cost Decimal Precision",
    )
    august = fields.Float(
        string="August",
        digits="Killing Cost Decimal Precision",
    )
    september = fields.Float(
        string="September",
        digits="Killing Cost Decimal Precision",
    )
    october = fields.Float(
        string="October",
        digits="Killing Cost Decimal Precision",
    )
    november = fields.Float(
        string="November",
        digits="Killing Cost Decimal Precision",
    )
    december = fields.Float(
        string="December",
        digits="Killing Cost Decimal Precision",
    )
