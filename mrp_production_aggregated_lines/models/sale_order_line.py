# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields, exceptions, _
from odoo.models import expression
from odoo.tools.safe_eval import safe_eval


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_selection_production_state(self):
        return self.env["mrp.production"].fields_get(
            allfields=["state"])["state"]["selection"]

    mrp_production_id = fields.Many2one(
        comodel_name="mrp.production", string="Production",
        copy=False)
    production_state = fields.Selection(
        string="Production State",
        selection="_get_selection_production_state",
        related="mrp_production_id.state",
        store=True)
    manufacturable_product = fields.Boolean(
        string="Is Product Manufacturable?",
        related="product_id.is_manufacturable",
        store=True,
        index=True)
    stock_qty = fields.Float(
        string="Qty to Manufacture for Stock",
        related="mrp_production_id.stock_qty",
        store=True)
    sale_line_qty = fields.Float(
        string="Sold Qty to Manufacture",
        related="mrp_production_id.sale_line_qty",
        store=True)

    def _action_mrp_dict(self):
        self.ensure_one()
        values = {
            "date_planned_start": self.order_id.date_order,
            "product_id": self.product_id.id or False,
            "product_qty": self.product_uom_qty,
            "product_uom_id": self.product_uom.id,
            "location_dest_id": self.order_id.warehouse_id.lot_stock_id.id,
            "active": False,
            "origin": self.order_id.name,
        }
        return values

    def _get_aggregable_mo_domain(self):
        return [
            ("product_id", "=", self.product_id.id or False),
            ("product_uom_id", "=", self.product_uom.id),
            ("location_dest_id", "=",
             self.order_id.warehouse_id.lot_stock_id.id),
            ("state", "=", "draft"),
            ("active", "=", False),
        ]
        # week = values.get("date_planned_start").isocalendar()[:2]
        # mo = mos.filtered(
        #     lambda x: week == x.date_planned_start.isocalendar()[:2])

    @api.multi
    def _aggregate_to_mo(self):
        self.ensure_one()
        mo_domain = self._get_aggregable_mo_domain()
        mo = self.env["mrp.production"].search(mo_domain, limit=1)
        if mo:
            self.mrp_production_id = mo.id
            mo.origin = mo._recalculate_origin()
            mo.with_context(sale_line_id=self.id)._update_mo_qty(
                self.product_uom_qty + mo.product_qty)
        return mo

    @api.multi
    def _action_launch_stock_rule(self):
        for line in self:
            super(SaleOrderLine,
                  line.with_context(
                      sale_line_id=line.id,
                      active=True,
                      production_id=line.mrp_production_id.id)
                  )._action_launch_stock_rule()
        return True

    @api.multi
    def action_create_mrp(self):
        if any(self.filtered(lambda l: l.product_uom_qty <= 0)):
            raise exceptions.Warning(_("The quantity must be positive."))
        mrp_orders = self.env["mrp.production"]
        for line in self:
            aggregated_mo = line._aggregate_to_mo()
            if not aggregated_mo:
                picking_type_id = line.order_id.warehouse_id.manu_type_id.id
                values = line._action_mrp_dict()
                aggregated_mo = self.env["mrp.production"].with_context(
                    default_picking_type_id=picking_type_id
                ).create(values)
                line.mrp_production_id = aggregated_mo.id
            mrp_orders |= aggregated_mo
        mrp_orders.action_compute()
            # mrp.with_context(sale_line_id=self.id).action_compute()

    @api.multi
    def button_create_mrp(self):
        self.ensure_one()
        self.action_create_mrp()

    @api.multi
    def action_detach_mo(self):
        for line in self:
            production = line.mrp_production_id
            if production.state == "draft":
                new_qty = production.product_qty - line.product_uom_qty
                if new_qty > 0:
                    production._update_mo_qty(new_qty)
                    production.sale_line_ids = [(3, line.id)]
                    production.origin = production._recalculate_origin()
                    production.action_compute()
                    line.mrp_production_id = False
                else:
                    line.mrp_production_id.action_cancel()
                    production.sale_line_ids = [(3, line.id)]
                    line.mrp_production_id = False


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_create_mrp_from_lines(self):
        for sale in self:
            for line in sale.order_line.filtered(
                    lambda x: not x.mrp_production_id and
                    x.manufacturable_product):
                try:
                    line.action_create_mrp()
                except exceptions.MissingError:
                    continue

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for line in self.mapped('order_line'):
            production = line.mrp_production_id
            if production and production.sale_line_ids == line:
                finished_workorders = production.workorder_ids.filtered(lambda w: w.state == 'done')
                if not finished_workorders:
                    production.action_cancel()
            else:
                if production:
                    production._update_mo_qty(production.product_qty -
                                              line.product_uom_qty)
                    production.sale_line_ids = [(3, line.id)]
        return res

    @api.multi
    def action_show_manufacturing_orders(self):
        self.ensure_one()
        action = self.env.ref("mrp.mrp_production_action")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(action_dict.get("context", "{}"))
        action_dict["context"].update({
            "active_test": False,
        })
        domain = expression.AND([
            [("sale_line_ids", "in", self.order_line.ids)],
        ])
        action_dict.update({
            "domain": domain,
        })
        return action_dict

    @api.multi
    def action_show_scheduled_products(self):
        self.ensure_one()
        action = self.env.ref(
            "mrp_scheduled_products.mrp_production_product_line_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND([
            [("production_id.sale_line_ids", "in", self.order_line.ids)],
        ])
        action_dict.update({
            "domain": domain,
        })
        return action_dict
