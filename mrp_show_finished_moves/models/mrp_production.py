# Copyright 2025 Lucía Echeverría - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_show_finished_move_lines(self):
        self.ensure_one()
        related_productions = self.env["mrp.production"].search(
            [("procurement_group_id", "=", self.procurement_group_id.id)]
        )
        finished_lines = related_productions.mapped("move_finished_ids.move_line_ids")
        return {
            "type": "ir.actions.act_window",
            "name": "Finished Move Lines",
            "view_mode": "tree",
            "res_model": "stock.move.line",
            "domain": [("id", "in", finished_lines.ids)],
            "context": {"default_procurement_group_id": self.procurement_group_id.id},
        }

    def action_show_finished_move_lines_result_packages(self):
        self.ensure_one()
        finished_lines_packages = self.mapped(
            "move_finished_ids.move_line_ids.result_package_id"
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Result Packages",
            "view_mode": "tree",
            "res_model": "stock.quant.package",
            "domain": [("id", "in", finished_lines_packages.ids)],
        }

    @api.depends(
        "workorder_ids.state", "move_finished_ids", "move_finished_ids.quantity_done"
    )
    def _get_produced_qty(self):
        for production in self:
            done_moves = production.move_finished_ids.filtered(
                lambda x: x.state != "cancel"
                and x.product_id.id == production.product_id.id
                and production.state == "done"
            )
            qty_produced = sum(done_moves.mapped("quantity_done"))
            production.qty_produced = qty_produced
        return True

    def button_mark_done(self):
        for production in self:
            finished_move = production.move_finished_ids.filtered(
                lambda m: m.product_id.id == production.product_id.id
            )
            if finished_move:
                quantity_done = finished_move.quantity_done
                if quantity_done != production.qty_producing and quantity_done != 0:
                    return self._launch_qty_warning(
                        production,
                        _(
                            "Producing vs Done quantity mismatch detected:\n\n"
                            "• Manufacturing Order reports %(planned)s units producing.\n"
                            "• Manufacturing Order finished moves report %(actual)s units\n"
                            "  produced.\n\n"
                            "If you choose 'Yes', the system will:\n"
                            "1. Set 'Quantity Producing' to match 'Quantity Done'.\n"
                            "2. Update all related WOs' 'Quantity Producing' and\n"
                            "   'Quantity Produced' to match 'Quantity Done'.\n"
                            "3. Continue marking the Manufacturing Order as done."
                        )
                        % {
                            "planned": production.qty_producing,
                            "actual": quantity_done,
                        },
                        yes_label=_("Yes, adjust quantities and proceed"),
                        no_label=_("No, review data first"),
                    )
                qty_produced_wo = finished_move.workorder_id.qty_produced
                if qty_produced_wo != quantity_done and quantity_done != 0:
                    return self._launch_qty_warning(
                        production,
                        _(
                            "Work Order vs Manufacturing Order quantity mismatch detected:\n\n"
                            "• Work Orders report %(wo_qty)s units produced.\n"
                            "• Manufacturing Order finished moves report %(mo_qty)s units\n"
                            "  produced.\n\n"
                            "If you choose 'Yes', the system will:\n"
                            "1. Set 'Quantity Producing' to match 'Quantity Done'.\n"
                            "2. Update all related Work Orders' 'Quantity Producing' and\n"
                            "   'Quantity Produced' to match 'Quantity Done'.\n"
                            "3. Continue marking the Manufacturing Order as done."
                        )
                        % {
                            "wo_qty": qty_produced_wo,
                            "mo_qty": quantity_done,
                        },
                        yes_label=_("Yes, adjust quantities and proceed"),
                        no_label=_("No, review data first"),
                    )
        return super().button_mark_done()

    def _launch_qty_warning(self, production, message, yes_label, no_label):
        """Launches the generic quantity warning wizard with context-specific text."""
        return {
            "name": _("Quantity Discrepancy Warning"),
            "type": "ir.actions.act_window",
            "res_model": "mrp.production.qty.warning",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_production_id": production.id,
                "default_warning_message": message,
                "default_yes_label": yes_label,
                "default_no_label": no_label,
            },
        }

    def update_quantity_done(self):
        for production in self:
            finished_move = production.move_finished_ids.filtered(
                lambda m: m.product_id == production.product_id
            )
            if finished_move:
                quantity_done = finished_move.quantity_done
                production.qty_producing = quantity_done
                production._onchange_producing()
                for wo in production.workorder_ids:
                    wo.qty_producing = quantity_done
                    wo.qty_produced = quantity_done


class MrpProductionQtyWarning(models.TransientModel):
    _name = "mrp.production.qty.warning"
    _description = "Inconsistency in Quants Warning"

    production_id = fields.Many2one("mrp.production")
    warning_message = fields.Text(readonly=True)
    yes_label = fields.Char(default="Yes")
    no_label = fields.Char(default="No")

    def action_yes(self):
        self.production_id.update_quantity_done()
        return self.production_id.button_mark_done()

    def action_no(self):
        return {"type": "ir.actions.act_window_close"}
