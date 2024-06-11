# Copyright 2018 Alfredo de la Fuente - Eider Oyarbide - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MrpProductionProductLine(models.Model):
    _inherit = "mrp.production.product.line"

    route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Route",
    )
    make_to_order = fields.Boolean(string="Make to order")
    date = fields.Date(string="Date")
    new_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Created Production Order",
    )
    production_date_planned_start = fields.Datetime(
        string="Deadline start",
        related="new_production_id.date_planned_start",
        related_sudo=True,
        store=True,
    )
    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Purchase order line",
    )
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase order",
        related="purchase_order_line_id.order_id",
        related_sudo=True,
        store=True,
    )
    purchase_date_order = fields.Datetime(
        string="Purchase Date",
        related="purchase_order_id.date_order",
        related_sudo=True,
        store=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        related="production_id.analytic_account_id",
        related_sudo=True,
        store=True,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        make_to_order = self.env.ref("stock.route_warehouse0_mto", False)
        buy = self.env.ref("purchase_stock.route_warehouse0_buy", False)
        manufacture = self.env.ref("mrp.route_warehouse0_manufacture", False)
        self.make_to_order = make_to_order in self.product_id.route_ids
        self.route_id = manufacture if manufacture in self.product_id.route_ids else buy

    @api.multi
    def button_create_purchase_manufacturing_order(self):
        self.ensure_one()
        if self.production_id.state != "draft":
            raise ValidationError(
                _(
                    "You are not allowed to create structure for a confirmed "
                    "manufacturing order."
                )
            )
        buy = self.env.ref("purchase_stock.route_warehouse0_buy", False)
        manufacture = self.env.ref("mrp.route_warehouse0_manufacture", False)
        origin_manufacture_order = (
            self.production_id.origin_production_id or self.production_id
        )
        if self.route_id.id == buy.id:
            self.create_automatic_purchase_order(
                origin_manufacture_order, self.production_id.level
            )
        if self.route_id.id == manufacture.id:
            self.create_automatic_manufacturing_order(
                origin_manufacture_order, self.production_id.analytic_account_id
            )

    def _get_po_values(self, rule):
        return {
            "company_id": self.production_id.company_id,
            "date_planned": self.production_id.date_planned_start,
            "priority": 1,
            "warehouse_id": (rule.warehouse_id or
                             self.production_id.picking_type_id.warehouse_id),
        }

    @api.multi
    def create_automatic_purchase_order(self, origin_manufacture_order, level):
        self.ensure_one()
        if self.production_id.state != "draft":
            raise ValidationError(
                _(
                    "You are not allowed to create a purchase order in a confirmed "
                    "manufacturing order."
                )
            )
        if not self.product_id.seller_ids:
            message = _(
                "There is no vendor associated to the product {}. "
                "Please define a vendor for this product."
            ).format(self.product_id.name)
            raise ValidationError(message)
        location = (
            self.production_id.location_src_id or
            self.env["stock.warehouse"].search([
                ("company_id", "=", self.env.user.company_id.id)], limit=1).lot_stock_id
        )
        rule = self.env["procurement.group"]._get_rule(self.product_id, location, {})
        if not rule:
            raise UserError(
                _(
                    'No procurement rule found in location "%s" for product "%s".\n '
                    "Check routes configuration."
                )
                % (location.display_name, self.product_id.display_name)
            )
        values = self._get_po_values(rule)
        rule.with_context(
            mrp_production_product_line=self,
            origin_production_id=origin_manufacture_order.id,
            level=self.production_id.level + 1,
            analytic_account_id=self.analytic_account_id.id,
        )._run_buy(
            self.product_id,
            self.product_qty,
            self.product_uom_id,
            location,
            self.product_id.name,
            self.production_id.name,
            values,
        )

    def _get_new_mo_values(self, origin_manufacture_order, analytic_account):
        values = {
            "origin_production_id": origin_manufacture_order.id,
            "level": self.production_id.level + 1,
            "product_qty": self.product_qty,
            "user_id": self.production_id.user_id.id,
        }
        if analytic_account:
            values["analytic_account_id"] = analytic_account.id
        return values

    @api.multi
    def create_automatic_manufacturing_order(
        self, origin_manufacture_order, analytic_account
    ):
        self.ensure_one()
        if self.production_id.state != "draft":
            raise ValidationError(
                _(
                    "You are not allowed to create a manufacturing order in a "
                    "confirmed manufacturing order."
                )
            )
        location = (
            self.production_id.location_src_id or
            self.env["stock.warehouse"].search([
                ("company_id", "=", self.env.user.company_id.id)], limit=1).lot_stock_id
        )
        rule = self.env["procurement.group"]._get_rule(self.product_id, location, {})
        warehouse = rule.warehouse_id or self.product_id.warehouse_id
        values = {
            "company_id": self.production_id.company_id,
            "date_planned_start": self.production_id.date_planned_start
            - relativedelta(days=self.product_id.produce_delay),
            "date_planned": self.production_id.date_planned_start
            - relativedelta(days=self.product_id.produce_delay),
            "warehouse_id": warehouse,
            "picking_type_id": warehouse.manu_type_id,
            "priority": 1,
        }
        rule.with_context(force_execution=True)._run_manufacture(
            self.product_id,
            self.product_qty,
            self.product_uom_id,
            location,
            self.product_id.name,
            self.production_id.name,
            values,
        )
        cond = [
            ("origin", "=", self.production_id.name),
            ("product_id", "=", self.product_id.id),
            ("active", "=", False),
            ("origin_production_id", "=", False),
        ]
        new_production = self.env["mrp.production"].search(cond, limit=1)
        if new_production:
            vals = self._get_new_mo_values(origin_manufacture_order, analytic_account)
            new_production.write(vals)
            self.new_production_id = new_production
            self.new_production_id.action_compute()
