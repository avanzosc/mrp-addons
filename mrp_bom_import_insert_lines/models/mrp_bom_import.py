import logging

from odoo import _, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MrpBomImport(models.Model):
    _inherit = "mrp.bom.import"

    def action_insert_lines(self):
        self.ensure_one()
        _logger.info("Starting action_insert_lines for import ID: %s", self.id)

        all_lines = self._get_import_lines()
        _logger.info("Total lines fetched for import: %s", len(all_lines))

        lines = all_lines.filtered(lambda x: x.state == "pass")
        _logger.info("Total valid lines to process: %s", len(lines))

        if not lines:
            _logger.warning("No valid lines to process for import ID: %s", self.id)
            raise ValidationError(_("No valid lines to process."))

        for line in lines:
            _logger.info(
                "Processing line ID: %s, product: %s",
                line.id,
                line.bom_product_id.display_name,
            )
            bom_line_values = line.generate_bom_line_values()
            _logger.debug(
                "Generated bom_line_values for line ID %s: %s", line.id, bom_line_values
            )

            for bom in line.bom_product_id.bom_ids:
                _logger.info(
                    "Inserting line into BoM ID: %s for product: %s",
                    bom.id,
                    line.bom_product_id.name,
                )
                self.env["mrp.bom.line"].create(bom_line_values)
                _logger.info(
                    "Created line for BoM ID %s (product: %s).",
                    bom.id,
                    line.bom_product_id.name,
                )

            line.write(
                {
                    "state": "done",
                }
            )
            _logger.info("Marked line ID %s as 'done'", line.id)

        _logger.info("Finished action_insert_lines for import ID: %s", self.id)
