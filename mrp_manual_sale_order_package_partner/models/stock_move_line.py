from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    partner_id = fields.Many2one("res.partner", string="Partner")

    @api.model_create_multi
    def create(self, vals_list):
        mls = super().create(vals_list)
        for ml in mls:
            if not ml.partner_id:
                if (
                    ml.move_id.production_id
                    and ml.move_id.production_id.manual_partner_id
                ):
                    ml.partner_id = ml.move_id.production_id.manual_partner_id
        return mls

    def _action_done(self):
        pending = [
            (ml.result_package_id, ml.move_id.production_id.manual_partner_id)
            for ml in self
            if ml.result_package_id
            and ml.move_id.production_id
            and not ml.result_package_id.partner_id
        ]
        res = super()._action_done()
        for package, partner in pending:
            if not package.partner_id:
                package.partner_id = partner
        return res
