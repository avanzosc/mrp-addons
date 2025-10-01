# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, models


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_start(self):
        self.ensure_one()
        if self.workcenter_id.is_external:
            return super().button_start()
        elif "from_wizard_button_start" in self.env.context:
            return self.button_start_customized()
        else:
            return {
                "type": "ir.actions.act_window",
                "name": _("Start Workorder"),
                "res_model": "wiz.update.workcenter.productivity",
                "view_mode": "form",
                "target": "new",
                "view_id": self.env.ref(
                    "mrp_productivity_employee.wiz_update_workcenter_productivity_form_view"
                ).id,
                "context": dict(
                    self.env.context,
                    default_workorder_id=self.id,
                    default_action_type="start",
                ),
            }

    def button_pending(self):
        if (
            "from_wizard_button_pending" in self.env.context
            or self.workcenter_id.is_external
        ):
            return super().button_pending()
        else:
            return {
                "type": "ir.actions.act_window",
                "name": _("Pause Workorder"),
                "res_model": "wiz.update.workcenter.productivity",
                "view_mode": "form",
                "target": "new",
                "view_id": self.env.ref(
                    "mrp_productivity_employee.wiz_update_workcenter_productivity_form_view"
                ).id,
                "context": dict(
                    self.env.context,
                    default_workorder_id=self.id,
                    default_action_type="pause",
                ),
            }

    def button_finish(self):
        if (
            "from_button_mark_done" in self.env.context
            or "from_wizard_button_finish" in self.env.context
        ):
            return super().button_finish()
        elif self.workcenter_id.is_external:
            return super().button_finish()
        else:
            return {
                "type": "ir.actions.act_window",
                "name": _("Finish Workorder"),
                "res_model": "wiz.update.workcenter.productivity",
                "view_mode": "form",
                "target": "new",
                "view_id": self.env.ref(
                    "mrp_productivity_employee.wiz_update_workcenter_productivity_form_view"
                ).id,
                "context": dict(
                    self.env.context,
                    default_workorder_id=self.id,
                    default_action_type="finish",
                ),
            }

    def _prepare_timeline_vals(self, duration, date_start, date_end=False):
        values = super()._prepare_timeline_vals(duration, date_start, date_end=date_end)
        if "default_employee_id" in self.env.context:
            values["employee_id"] = self.env.context.get("default_employee_id")
        if "default_loss_id" in self.env.context:
            values["loss_id"] = self.env.context.get("default_loss_id")
        return values

    def button_start_customized(self):
        self.ensure_one()
        if self.state in ("done", "cancel"):
            return True
        if self.production_id.state != "progress":
            self.production_id.write(
                {
                    "date_start": datetime.now(),
                }
            )
        if self.product_tracking == "serial" and self.qty_producing == 0:
            self.qty_producing = 1.0
        elif self.qty_producing == 0:
            self.qty_producing = self.qty_remaining

        if self._should_start_timer():
            self.env["mrp.workcenter.productivity"].create(
                self._prepare_timeline_vals(self.duration, datetime.now())
            )
        start_date = datetime.now()
        vals = {
            "state": "progress",
            "date_start": start_date,
        }
        if not self.leave_id:
            leave = self.env["resource.calendar.leaves"].create(
                {
                    "name": self.display_name,
                    "calendar_id": self.workcenter_id.resource_calendar_id.id,
                    "date_from": start_date,
                    "date_to": start_date
                    + relativedelta(minutes=self.duration_expected),
                    "resource_id": self.workcenter_id.resource_id.id,
                    "time_type": "other",
                }
            )
            vals["leave_id"] = leave.id
            return self.write(vals)
        else:
            if not self.date_planned_start or self.date_planned_start > start_date:
                vals["date_planned_start"] = start_date
                vals["date_planned_finished"] = self._calculate_date_planned_finished(
                    start_date
                )
            if self.date_planned_finished and self.date_planned_finished < start_date:
                vals["date_planned_finished"] = start_date
            return self.with_context(bypass_duration_calculation=True).write(vals)
