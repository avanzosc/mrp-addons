from odoo import models


class ChangeProductionQty(models.TransientModel):

    _inherit = "change.production.qty"

    def change_prod_qty(self):
        for wizard in self:
            production = wizard.mo_id
            if production.product_id.tracking == "serial":
                production.move_finished_ids.filtered(
                    lambda m: m.product_id == production.product_id
                ).action_clear_lines_show_details()
                res = super().change_prod_qty()
                production._update_move_next_serial()
            else:
                res = super().change_prod_qty()
        return res
