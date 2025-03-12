# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    lot_average_price = fields.Float(readonly=True, group_operator="avg")
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        readonly=True,
    )
    price_unit = fields.Float(readonly=True, group_operator="avg")
    lot_cost = fields.Float(
        readonly=True,
    )
    difference = fields.Float(
        readonly=True,
    )
    surplus = fields.Boolean(
        readonly=True,
    )

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale(groupby)
        res += """, l.lot_id"""
        res += """, l.price_unit"""
        res += """, l.lot_average_price"""
        res += """, l.surplus"""
        return res

    def _select_additional_fields(self, fields):
        fields["lot_id"] = ", l.lot_id as lot_id"
        fields["price_unit"] = ", l.price_unit as price_unit"
        fields["lot_average_price"] = ", l.lot_average_price as lot_average_price"
        fields["surplus"] = ", l.surplus as surplus"
        return super()._select_additional_fields(fields)

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if not fields:
            fields = {}
        fields["lot_cost"] = ", sum(l.lot_cost / u.factor * u2.factor) as " "lot_cost"
        fields["difference"] = (
            ", sum(l.price_subtotal - l.lot_cost / u.factor * u2.factor) as "
            "difference"
        )
        return super(SaleReport, self)._query(
            with_clause=with_clause,
            fields=fields,
            groupby=groupby,
            from_clause=from_clause,
        )
