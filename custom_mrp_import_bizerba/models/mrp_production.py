# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

import pymssql
import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base_import_wizard.models.base_import import IMPORT_STATUS


class MrpProduction(models.Model):
    _name = "mrp.production"
    _inherit = ["mrp.production", "base.import", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute=False)
    data = fields.Binary(required=False)
    import_line_ids = fields.One2many(
        comodel_name="bizerba.import.line",
        inverse_name="production_id",
    )
    import_state = fields.Selection(
        selection=IMPORT_STATUS,
        compute="_compute_import_state",
        string="Import Status",
        store=True,
    )

    @api.depends(
        "import_line_ids",
        "import_line_ids.state",
    )
    def _compute_import_state(self):
        for production in self:
            lines = production.import_line_ids
            line_states = lines.mapped("state")
            if line_states and any([state == "error" for state in line_states]):
                production.import_state = "error"
            elif line_states and all([state == "done" for state in line_states]):
                production.import_state = "done"
            elif line_states and all([state == "pass" for state in line_states]):
                production.import_state = "pass"
            elif lines:
                production.import_state = "2validate"
            else:
                production.import_state = "draft"

    def action_conect_with_bizerba(self):
        self.ensure_one()
        self.import_line_ids.unlink()
        self.action_confirm()
        if (
            not self.clasified_date
            or not self.clasified_time_start
            and not self.clasified_time_stop
        ):
            raise ValidationError(
                _("This classification does not have a start/end " + "time or date.")
            )
        if not self.lot_producing_id:
            raise ValidationError(_("This classification does not have the lot."))
        date = self.clasified_date
        time_start = self.clasified_time_start
        if time_start == 0:
            date = date - timedelta(days=1)
        time_start = "{:02.0f}:{:02.0f}".format(*divmod(time_start * 60, 60))
        time_start = datetime.strptime(time_start, "%H:%M")
        time_start = time_start - timedelta(minutes=1)
        time_start = time_start.time()
        time_stop = self.clasified_time_stop
        time_stop = "{:02.0f}:{:02.0f}".format(*divmod(time_stop * 60, 60))
        time_stop = datetime.strptime(time_stop, "%H:%M").time()
        start_date = "{} {}".format(date, time_start)
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        if time_start > time_stop:
            date = date + timedelta(days=1)
        stop_date = "{} {}".format(date, time_stop)
        stop_date = datetime.strptime(stop_date, "%Y-%m-%d %H:%M:%S")
        try:
            conn = pymssql.connect(
                server=r"192.168.201.3\SQLEXPRESS",
                user="integracion",
                password="ew#211218",
                database="BCT2DB",
            )
            cursor = conn.cursor()
            query = (
                "SELECT * FROM [Pesada Individual] as p "
                "WHERE LEFT(p.GT1F,4)+'-'+SUBSTRING(p.GT1F,5,2)+'-'"
                "+SUBSTRING(p.GT1F,7,2)+' '+SUBSTRING(p.GT1F,10,2)+"
                "':'+RIGHT(p.GT1F,2)+':00' BETWEEN '"
                + str(start_date)
                + "' AND '"
                + str(stop_date)
                + "'"
            )
            cursor.execute(query)
            row = cursor.fetchone()
            while row:
                if str(self.lot_producing_id.name) == str(row[8]):
                    line_lot = row[8]
                    line_product_code = row[9]
                    line_product_qty = row[10]
                    line_product_qty = line_product_qty.split(";")
                    line_uom = line_product_qty[0]
                    line_product_qty = float(line_product_qty[2]) * pow(
                        10, float(line_product_qty[1])
                    )
                    line_chicken_code = row[12]
                    line_date = row[13]
                    line_date = datetime.strptime(line_date, "%Y%m%d-%H%M")
                    log_info = ""
                    timezone = pytz.timezone(self._context.get("tz") or "UTC")
                    line_date = timezone.localize(line_date).astimezone(pytz.UTC)
                    line_date = line_date.replace(tzinfo=None)
                    line_data = {
                        "import_id": self.id,
                        "production_id": self.id,
                        "line_lot": line_lot,
                        "line_product_code": line_product_code,
                        "line_product_qty": line_product_qty,
                        "line_uom": line_uom,
                        "line_chicken_code": line_chicken_code,
                        "line_date": line_date,
                        "log_info": log_info,
                    }
                    self.import_line_ids = [(0, 0, line_data)]
                row = cursor.fetchone()
            conn.close()
            if self.state == "draft":
                self.production_id.action_confirm()
            if self.import_line_ids:
                self.action_validate()
        except Exception:
            raise ValidationError(_("The connection could not be established."))
