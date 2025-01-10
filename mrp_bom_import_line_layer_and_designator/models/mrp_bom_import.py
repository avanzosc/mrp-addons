from odoo import _, models

from odoo.addons.mrp_bom_import.models.mrp_bom_import import convert2str


class MrpBomImport(models.Model):
    _inherit = "mrp.bom.import"

    def _get_line_values(self, row_values):
        res = super()._get_line_values(row_values)
        res.update(
            {
                "layer": convert2str(row_values.get("Layer", "")),
                "designator": convert2str(row_values.get("Designator", "")),
            }
        )
        return res

    def action_update_layer_and_designator(self):
        BomLine = self.env["mrp.bom.line"]

        for record in self:
            for line in record.bom_line_import_ids:

                layer, designator = convert2str(line.layer), convert2str(
                    line.designator
                )
                search_domain = [
                    ("product_id", "=", line.product_id.id),
                    (
                        "bom_id.product_tmpl_id",
                        "=",
                        line.bom_product_id.product_tmpl_id.id,
                    ),
                    "|",
                    ("bom_id.product_id", "=", line.bom_product_id.id),
                    ("bom_id.product_id", "=", False),
                ]

                bom_lines = BomLine.search(search_domain)

                if bom_lines:
                    for bom_line in bom_lines:
                        line.log_info = _("Found BOM Line")

                        if layer and bom_line.layer in [False, None, ""]:
                            bom_line.layer = layer
                            line.log_info = _("Layer updated to '%s'") % layer
                            line.state = "done"
                        else:
                            if not layer:
                                line.log_info = _("No layer provided")
                            elif bom_line.layer not in [False, None, ""]:
                                line.log_info = (
                                    _("Layer already set to '%s'") % bom_line.layer
                                )

                        if designator and bom_line.designator in [False, None, ""]:
                            bom_line.designator = designator
                            line.log_info = _("Designator updated to '%s'") % designator
                            line.state = "done"
                        else:
                            if not designator:
                                line.log_info = _("No designator provided")
                            elif bom_line.designator not in [False, None, ""]:
                                line.log_info = (
                                    _("Designator already set to '%s'")
                                    % bom_line.designator
                                )

                else:
                    line.log_info = _("No BOM lines found\n%s") % str(search_domain)
                    line.state = "error"
