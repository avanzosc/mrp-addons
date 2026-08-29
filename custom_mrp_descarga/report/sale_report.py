# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    lot_average_price = fields.Float(readonly=True, aggregator="avg")
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        readonly=True,
    )
    price_unit = fields.Float(readonly=True, aggregator="avg")
    lot_cost = fields.Float(
        readonly=True,
    )
    difference = fields.Float(
        readonly=True,
    )
    surplus = fields.Boolean(
        readonly=True,
    )
    commitment_date = fields.Datetime(string="Delivery Date", readonly=True)

    def action_view_sale_report(self):
        context = self.env.context.copy()
        cron = self.env.ref("custom_mrp_descarga.ir_cron_recalculate_lot_avergae_cost")
        if cron:
            cron.method_direct_trigger()
        return {
            "name": _("Sale Report"),
            "view_mode": "pivot",
            "res_model": "sale.report",
            "type": "ir.actions.act_window",
            "context": context,
        }

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            l.lot_id,
            l.lot_average_price,
            l.surplus,
            s.commitment_date"""
        return res

    def _select_additional_fields(self):
        fields = super()._select_additional_fields()
        fields["lot_id"] = "l.lot_id"
        fields["lot_average_price"] = "l.lot_average_price"
        fields["surplus"] = "l.surplus"
        fields["commitment_date"] = "s.commitment_date"
        fields["lot_cost"] = "SUM(l.lot_cost / u.factor * u2.factor)"
        fields["difference"] = (
            "SUM(l.price_subtotal - l.lot_cost / u.factor * u2.factor)"
        )
        return fields
