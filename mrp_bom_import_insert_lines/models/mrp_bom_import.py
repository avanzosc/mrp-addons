import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class MrpBomImport(models.Model):
    _inherit = "mrp.bom.import"

    def action_insert_lines(self):
        for line in self.bom_line_import_ids.filtered(
            lambda x: x.state == "pass" and x.bom_id
        ):
            _logger.info(
                "Processing line ID: %s, product: %s",
                line.id,
                line.product_id.display_name,
            )
            bom_line_values = line.generate_bom_line_values()
            bom_line_values.update({"bom_id": line.bom_id.id})
            _logger.info(
                "Generated bom_line_values for line ID %s: %s", line.id, bom_line_values
            )
            bom_line = self.env["mrp.bom.line"].create(bom_line_values)
            _logger.info(
                "Created BoM line ID %s for BoM ID %s (product: %s).",
                bom_line.id,
                line.bom_id.id,
                line.bom_product_id.name,
            )
            line.write(
                {
                    "bom_line_id": bom_line.id,
                    "state": "done",
                    "sequence": 100,
                }
            )
            _logger.info("Marked line ID %s as 'done'", line.id)

        _logger.info("Finished action_insert_lines for import ID: %s", self.id)


class MrpBomLineImport(models.Model):
    _inherit = "mrp.bom.line.import"

    validated_line = fields.Boolean(
        string="Validated",
        compute="_compute_validated_line",
        store=False,
    )

    @api.depends("state")
    def _compute_validated_line(self):
        for line in self:
            line.validated_line = line.state in ("pass", "done")

    def action_validate_lines(self):
        for line in self.filtered(lambda x: x.state not in ("done")):
            line_vals = {}
            log_info = ""
            product = bom_product = bom = False

            product, product_log_info = line._check_product()
            if product_log_info:
                log_info += product_log_info

            bom_product, bom_product_log_info = line._check_bom_product()
            if bom_product_log_info:
                log_info += bom_product_log_info

            if not line.quantity:
                log_info += _("Error: Quantity cannot be 0.")

            if product and bom_product and product.id == bom_product.id:
                log_info += _("Error: Product and BOM product are the same")

            if bom_product and line.bom_ref:
                bom_domain = [
                    ("product_tmpl_id", "=", bom_product.product_tmpl_id.id),
                    ("code", "=", line.bom_ref),
                ]
                boms = self.env["mrp.bom"].search(bom_domain)
                if boms:
                    bom = boms[-1]

            state = "error" if log_info else "pass"
            line_vals.update(
                {
                    "product_id": product and product.id,
                    "bom_product_id": bom_product and bom_product.id,
                    "bom_id": bom and bom.id,
                    "state": state,
                    "log_info": log_info,
                }
            )
            line.write(line_vals)
