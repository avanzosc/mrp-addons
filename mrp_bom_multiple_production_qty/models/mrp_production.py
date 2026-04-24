# (c) José A. Ballate - Guadaltech
# (c) Ignacio Ales López - Guadaltech
# (c) 2024 Alfredo de la Fuente - Avanzosc
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from math import floor

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @staticmethod
    def _calculate_multiple_amount_per_bom(product_qty, bom):
        """
        _calculate_multiple_amount_per_bom Retorna la nueva cantidad del
         producto según el múltiplo de la LdM.

        Calcula la cantidad que debe tener la producción según los múltiplos
         indicados en ésta. La fórmula que sigue el sistema es calcular el
         módulo de la producción actual en base al múltiplo

        :param product_qty: Cantidad a producir original
        :type product_qty: float
        :param bom: Lista de materiales en la que se va a producir y se
         consultará el múltiplo.
        :type bom: recordset("mrp.bom")
        :return: Cantidad nueva de la produccción. En caso de ser múltiplo o no
        ser necesario, será la misma que la original.
        :rtype: float
        """
        result = product_qty

        # Comprobamos que haya un valor válido o que la cantidad a producir no
        # sea menor a la cantidad múltiple.
        if bom.production_multiple > 0.0 and product_qty > 0:
            # Ejecutamos el módulo con respecto a los múltiplos
            mod_product_qty = product_qty % bom.production_multiple
            # Si es cero, es un múltiplo y lo dejamos así.
            if mod_product_qty != 0:
                # En caso contrario, tenemos que encontrar el múltiplo más cercano.
                result = bom.production_multiple * (
                    floor(product_qty / bom.production_multiple) + 1
                )

        return result

    @api.depends("bom_id")
    def _compute_product_qty(self):
        result = super()._compute_product_qty()
        for production in self.filtered(lambda x: x.state == "draft"):
            production.product_qty = MrpProduction._calculate_multiple_amount_per_bom(
                self.product_qty, self.bom_id
            )
        return result

    @api.onchange("product_qty")
    def _onchange_product_qty_multiple(self):
        if self.product_qty:
            self.product_qty = MrpProduction._calculate_multiple_amount_per_bom(
                self.product_qty, self.bom_id
            )
