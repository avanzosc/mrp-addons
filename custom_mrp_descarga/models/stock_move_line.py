# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    performance = fields.Float(
        string="Performance", compute="_compute_performance", store=True
    )
    sequence = fields.Integer(
        string="Sequence", compute="_compute_sequence", store=True
    )
    quartering = fields.Boolean(
        string="Quartering", related="production_id.quartering", store=True
    )
    saca_date = fields.Date(string="Saca Date", related="saca_line_id.date", store=True)
    qty_done = fields.Float(
        digits="Weight Decimal Precision",
    )
    average_price = fields.Float(string="Average Price", related="lot_id.average_price")

    @api.depends("production_id")
    def _compute_sequence(self):
        for line in self:
            sequence = 0
            if line.production_id:
                ids = []
                movelines = False
                if line in line.production_id.move_line_ids and (
                    line.location_id == (line.production_id.location_src_id)
                ):
                    movelines = line.production_id.move_line_ids
                elif line in line.production_id.finished_move_line_ids:
                    movelines = line.production_id.finished_move_line_ids
                if movelines:
                    for record in movelines:
                        if record.id not in ids:
                            ids.append(record.id)
                    if line.id in ids:
                        sequence = ids.index(line.id) + 1
            line.sequence = sequence

    @api.depends("production_id.consume_qty", "qty_done")
    def _compute_performance(self):
        for line in self:
            performance = 0
            if line.production_id and line.production_id.consume_qty != 0:
                performance = (line.qty_done * 100) / line.production_id.consume_qty
            line.performance = performance

    @api.onchange("reader")
    def onchange_reader(self):
        if self.reader:
            if (
                len(self.reader) == 44
                and self.reader[16] == "1"
                and self.reader[17] == "5"
            ):
                self.reader_44_15(reader=self.reader)
            elif (
                len(self.reader) == 46
                and self.reader[16] == "3"
                and self.reader[17] == "1"
            ):
                self.reader_46_31(reader=self.reader)
            else:
                message = _("Unidentified barcode format : %(reader)s") % {
                    "reader": self.reader,
                }
                raise ValidationError(message)

    def reader_44_15(self, reader):
        self.ensure_one()
        if reader and len(reader) == 44 and reader[16] == "1" and reader[17] == "5":
            product_code = reader[5:15]
            product_code = product_code.lstrip("0")
            product_domain = [("default_code", "=", product_code)]
            product = (
                self.env["product.product"]
                .search(product_domain)
                .filtered(
                    lambda c: c.company_id == self.company_id
                    or self.company_id in c.company_ids
                )
            )
            if not product:
                message = _(
                    "Product not found, reader information for product code: %(reader)s"
                ) % {
                    "reader": product_code,
                }
                raise ValidationError(message)
            self.product_id = product.id
            expiration_date = reader[18:24]
            timezone = pytz.timezone(self._context.get("tz") or "UTC")
            expiration_date = datetime.strptime(expiration_date, "%y%m%d")
            expiration_date = timezone.localize(expiration_date).astimezone(pytz.UTC)
            expiration_date = expiration_date.replace(tzinfo=None)
            qty_done = reader[28:31]
            qty_done_decimal = reader[31:34]
            qty_done = qty_done + "." + qty_done_decimal
            qty_done = float(qty_done)
            lot_name = reader[36:44]
            lot_domain = [
                ("name", "=", lot_name),
                ("company_id", "=", self.company_id.id),
                ("product_id", "=", product.id),
            ]
            lot = self.env["stock.production.lot"].search(lot_domain)
            if not lot:
                lot = self.env["stock.production.lot"].action_create_lot(
                    product, lot_name, self.company_id
                )
            self.write(
                {
                    "expiration_date": expiration_date,
                    "qty_done": qty_done,
                    "lot_id": lot.id,
                }
            )

    def reader_46_31(self, reader):
        self.ensure_one()
        if reader and len(reader) == 46 and reader[16] == "3" and reader[17] == "1":
            product_code = reader[5:15]
            product_code = product_code.lstrip("0")
            product_domain = [("default_code", "=", product_code)]
            product = (
                self.env["product.product"]
                .search(product_domain)
                .filtered(
                    lambda c: c.company_id == self.company_id
                    or self.company_id in c.company_ids
                )
            )
            if not product:
                message = _(
                    "Product not found, reader information for product code: %(reader)s"
                ) % {
                    "reader": product_code,
                }
                raise ValidationError(message)
            self.product_id = product.id
            qty_done = reader[20:23]
            qty_done_decimal = reader[23:26]
            qty_done = qty_done + "." + qty_done_decimal
            container = int(reader[28:36])
            lot_name = reader[38:46]
            lot_domain = [
                ("name", "=", lot_name),
                ("company_id", "=", self.company_id.id),
                ("product_id", "=", product.id),
            ]
            lot = self.env["stock.production.lot"].search(lot_domain)
            if not lot:
                lot = self.env["stock.production.lot"].action_create_lot(
                    product, lot_name, self.company_id
                )
            vals = {"container": container, "qty_done": qty_done, "lot_id": lot.id}
            self.write(vals)

    @api.onchange("unit")
    def onchange_unit(self):
        super(StockMoveLine, self).onchange_unit()
        if self.unit:
            self.download_unit = self.unit

    @api.onchange(
        "product_id",
        "location_id",
        "location_dest_id",
        "production_id",
        "production_id",
        "production_id",
    )
    def onchange_product_id(self):
        self.ensure_one()
        if (
            "production_id" in self.env.context
            or "default_production_id" in (self.env.context)
            and self.product_id
            and (self.location_id)
            and self.location_dest_id
        ):
            if "production_id" in self.env.context:
                production = self.env["mrp.production"].search(
                    [("id", "=", self.env.context["production_id"])]
                )
            if "default_production_id" in self.env.context:
                production = self.env["mrp.production"].search(
                    [("id", "=", self.env.context["default_production_id"])]
                )
            moves = production.move_raw_ids + production.move_byproduct_ids
            move = moves.filtered(
                lambda c: c.product_id == self.product_id
                and (c.location_id == self.location_id)
                and (c.location_dest_id == self.location_dest_id)
            )
            if move:
                self.move_id = move[:1].id

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        result = super(StockMoveLine, self)._onchange_lot_id()
        if (
            self.production_id
            and (self.production_id.bring_cost_from_lots)
            and (self.lot_id)
        ):
            self.standard_price = self.lot_id.average_price
        if (
            self.production_id
            and self.production_id.filter_only_entry_lots
            and self.location_dest_id == self.production_id.location_src_id
            and self.lot_id
        ):
            lot = self.lot_id.name
            if not any(
                [
                    line.lot_id.name == lot
                    for line in (
                        self.production_id.move_line_ids.filtered(
                            lambda c: c.location_id != self.location_id
                        )
                    )
                ]
            ):
                raise ValidationError(
                    _("The outgoing lot must match the incoming one.")
                )
        return result

    @api.onchange("lot_id", "product_id")
    def onchange_product_lot(self):
        if (
            self.product_id
            and (self.lot_id)
            and (self.product_id != self.lot_id.product_id)
        ):
            raise ValidationError(
                _(
                    "The product of the lot does not match with the "
                    + "product of the line."
                )
            )

    @api.model
    def create(self, values):
        if "qty_done" in values:
            move = self.env["stock.move"].browse(values.get("move_id"))
            if move.state == "cancel" and values.get("qty_done") != 0:
                move.state = "done"
                for line in move.move_line_ids:
                    line.state = "done"
        return super(StockMoveLine, self).create(values)

    def write(self, values):
        result = super(StockMoveLine, self).write(values)
        for line in self:
            if not line.location_id:
                values.update(
                    {
                        "location_id": line.move_id.location_id.id,
                        "location_dest_id": line.move_id.location_dest_id.id,
                    }
                )
        if "qty_done" in values:
            for line in self:
                if line.move_id.state == "cancel" and values.get("qty_done") != 0:
                    line.move_id.state = "done"
                    line.state = "done"
        return result
