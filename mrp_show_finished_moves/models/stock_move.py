from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()
        action["target"] = "current"
        action["context"] = action.get("context", {})

        if (
            self.production_id
            and not self.raw_material_production_id
            and self.product_id.tracking != "none"
        ):
            action["context"]["show_lot_name_instead_lot_id"] = True

        return action

    @api.onchange("quantity_done")
    def _on_change_quantity_done(self):
        for move in self:
            if move.production_id.qty_producing == 0.0:
                move.production_id.qty_producing = move.quantity_done

    @api.depends(
        "has_tracking",
        "picking_type_id.use_create_lots",
        "picking_type_id.use_existing_lots",
        "state",
    )
    def _compute_display_assign_serial(self):
        res = super()._compute_display_assign_serial()
        for move in self:
            if (
                not move.raw_material_production_id
                and move.product_id.tracking == "serial"
                and move.production_id
                and move.production_id.product_id == move.product_id
            ):
                move.display_assign_serial = True
        return res

    def action_show_move_lines_packages(self):
        self.ensure_one()
        origin_packages = self.mapped("move_line_ids.package_id")
        result_packages = self.mapped("move_line_ids.result_package_id")
        all_packages = (origin_packages | result_packages).filtered(lambda p: p)
        return {
            "type": "ir.actions.act_window",
            "name": "Packages",
            "view_mode": "tree",
            "res_model": "stock.quant.package",
            "domain": [("id", "in", all_packages.ids)],
        }

    def write(self, vals):
        res = super().write(vals)
        for move in self:
            if (
                move.product_id.tracking == "serial"
                and "next_serial_count" in vals
                and move.product_id == move.production_id.product_id
                and move.state not in ["done", "cancel"]
            ):
                production = move.production_id
                production._compute_last_manufactured_lot()
                if production.last_manufactured_lot:
                    next_serial = production._increment_serial_number(
                        production.last_manufactured_lot
                    )
                    move.next_serial = next_serial
                    move.action_clear_lines_show_details()
                    move.action_assign_serial_show_details()
                if production.qty_producing != move.quantity_done:
                    production.qty_producing = move.quantity_done
        return res
