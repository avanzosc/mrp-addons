# Copyright 2026 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_see_attachments(self):
        r"""
        Método nuevo. Botón con apertura de wizard.

        Este método muestra la información relacionada con los adjuntos del
        producto de esta línea de movimiento.
        Para mostrar la información, accede al método del objeto padre
        "stock.move" o movimiento de stock.
        """
        return self.move_id.action_see_attachments()
