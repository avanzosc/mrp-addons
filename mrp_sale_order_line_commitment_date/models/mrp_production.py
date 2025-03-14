import re

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_order_line_commitment_date = fields.Date(
        compute="_compute_sale_order_line_commitment_date",
        string="Commitment Date",
        store=True,
        readonly=True,
        help="Commitment Date from the related Sale Order Line",
    )

    def _get_sale_order(self, origin):
        """Gets the sale order associated with the 'origin'."""
        match = re.match(r"SO(\d+)", origin)
        if match:
            sale_order_name = match.group(0)
            return self.env["sale.order"].search(
                [("name", "=", sale_order_name)], limit=1
            )
        return False

    def _get_sale_order_line_commitment_date(self, sale_order):
        """Gets the earliest commitment date from the sale order lines."""
        if sale_order and sale_order.order_line:
            commitment_dates = sale_order.order_line.mapped("commitment_date")
            if commitment_dates:
                earliest_commitment_date = min(commitment_dates)
                return earliest_commitment_date
        return False

    def _compute_sale_order_line_commitment_date(self):
        for record in self:
            if record.origin:
                sale_order = record._get_sale_order(record.origin)
                new_commitment_date = record._get_sale_order_line_commitment_date(
                    sale_order
                )
                if record.sale_order_line_commitment_date != new_commitment_date:
                    record.sale_order_line_commitment_date = new_commitment_date
            else:
                if record.sale_order_line_commitment_date:
                    record.sale_order_line_commitment_date = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "origin" in vals:
                sale_order = self._get_sale_order(vals["origin"])
                vals["sale_order_line_commitment_date"] = (
                    self._get_sale_order_line_commitment_date(sale_order)
                )
        return super().create(vals_list)

    def write(self, vals):
        if "origin" in vals:
            sale_order = self._get_sale_order(vals["origin"])
            vals["sale_order_line_commitment_date"] = (
                self._get_sale_order_line_commitment_date(sale_order)
            )
        
        res = super().write(vals)

        # Update related child productions
        if "sale_order_line_commitment_date" in vals:
            child_productions = self._get_children()
            for child_production in child_productions:
                child_production.sale_order_line_commitment_date = vals[
                    "sale_order_line_commitment_date"
                ]

        return res
