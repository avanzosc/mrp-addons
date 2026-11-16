# Copyright 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"

    def button_start(self, raise_on_invalid_state=False):
        self.ensure_one()
        if "from_wizard_button_start" not in self.env.context:
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
        if any(wo.working_state == "blocked" for wo in self):
            raise UserError(
                _("Please unblock the work center to start the work order.")
            )
        for wo in self:
            if wo.state in ("done", "cancel"):
                if raise_on_invalid_state:
                    continue
                raise UserError(
                    _("You cannot start a work order that is already done or cancelled")
                )
            if wo.product_tracking == "serial" and wo.qty_producing == 0:
                wo.qty_producing = 1.0
            elif wo.qty_producing == 0:
                wo.qty_producing = wo.qty_remaining

            if wo._should_start_timer():
                self.env["mrp.workcenter.productivity"].create(
                    wo._prepare_timeline_vals(wo.duration, fields.Datetime.now())
                )
            if wo.production_id.state != "progress":
                wo.production_id.write({"date_start": fields.Datetime.now()})
            if wo.state == "progress":
                continue
            date_start = fields.Datetime.now()
            vals = {
                "state": "progress",
                "date_start": date_start,
            }
            if not wo.leave_id:
                leave = self.env["resource.calendar.leaves"].create(
                    {
                        "name": wo.display_name,
                        "calendar_id": wo.workcenter_id.resource_calendar_id.id,
                        "date_from": date_start,
                        "date_to": date_start
                        + relativedelta(minutes=wo.duration_expected),
                        "resource_id": wo.workcenter_id.resource_id.id,
                        "time_type": "other",
                    }
                )
                vals["date_finished"] = leave.date_to
                vals["leave_id"] = leave.id
                wo.write(vals)
            else:
                if not wo.date_start or wo.date_start > date_start:
                    vals["date_start"] = date_start
                    vals["date_finished"] = wo._calculate_date_finished(date_start)
                if wo.date_finished and wo.date_finished < date_start:
                    vals["date_finished"] = date_start
                wo.with_context(bypass_duration_calculation=True).write(vals)

    def button_pending(self):
        if "from_wizard_button_pending" in self.env.context:
            return super(MrpWorkorder, self.sudo()).button_pending()
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
            return super(MrpWorkorder, self.sudo()).button_finish()
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
        if self.env.context.get("employee_id_ctx", False):
            values["employee_id"] = self.env.context.get("employee_id_ctx")
        if self.env.context.get("loss_id_ctx", False):
            values["loss_id"] = self.env.context.get("loss_id_ctx")
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

    def _domain_mrp_workcenter_productivity(self, doall):
        if "default_employee_id" not in self.env.context:
            return super()._domain_mrp_workcenter_productivity(doall)
        else:
            domain = [("workorder_id", "in", self.ids), ("date_end", "=", False)]
            if not doall:
                domain = expression.AND(
                    [
                        domain,
                        [
                            (
                                "employee_id",
                                "=",
                                self.env.context.get("default_employee_id").id,
                            )
                        ],
                    ]
                )
            return domain
