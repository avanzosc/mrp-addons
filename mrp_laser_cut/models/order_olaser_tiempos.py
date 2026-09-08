# Copyright 2026 Inael
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class OrderOlaserTiempos(models.Model):
    _name = "order.olaser.tiempos"
    _description = "Laser Cutting Order Times"

    laser_tiempos_id = fields.Many2one(
        comodel_name="order.olaser", string="Laser Order"
    )
    employee_id = fields.Many2one(comodel_name="hr.employee")
    entrada = fields.Datetime(string="Start")
    salida = fields.Datetime(string="End")
    tiempo = fields.Float(
        string="Duration (HH:MM)", compute="_compute_tiempo", store=True
    )
    estado = fields.Selection(
        selection=[
            ("pendiente", "Pending"),
            ("cerrada", "Closed"),
            ("cancelada", "Cancelled"),
            ("interrumpida", "Interrupted"),
            ("activa", "Active"),
        ],
        string="Status",
        default="pendiente",
        required=True,
    )
    comunicado = fields.Float(string="Reported Quantity", default=0)

    @api.depends("entrada", "salida")
    def _compute_tiempo(self):
        for record in self:
            if record.entrada and record.salida:
                delta = record.salida - record.entrada
                record.tiempo = delta.total_seconds() / 3600.0
            else:
                record.tiempo = 0
