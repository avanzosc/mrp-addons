from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        related="result_package_id.partner_id",
    )

    def _action_done(self):
        res = super()._action_done()
        for ml in self:
            if (
                ml.result_package_id
                and ml.move_id.production_id
                and not ml.result_package_id.partner_id
            ):
                ml.result_package_id.partner_id = (
                    ml.move_id.production_id.manual_partner_id
                )
        return res
