# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, _
from odoo.exceptions import Warning as UserError
from odoo.tools import float_round


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _prepare_consume_line(self, bom_line, quantity, product,
                              original_qty, parent_line):
        return (bom_line,
                {'qty': quantity,
                 'product': product,
                 'original_qty': original_qty,
                 'parent_line': parent_line})

    @api.model
    def _bom_find_prepare(self, product_tmpl=None, product=None,
                          picking_type=None, company_id=False):
        return self._bom_find(product_tmpl=product_tmpl, product=product,
                              picking_type=picking_type, company_id=company_id)

    def explode(self, product, quantity, picking_type=False):
        """
            Explodes the BoM and creates two lists with all the information you need: bom_done and line_done
            Quantity describes the number of times you need the BoM: so the quantity divided by the number created by the BoM
            and converted into its UoM
        """
        from collections import defaultdict

        graph = defaultdict(list)
        V = set()

        def check_cycle(v, visited, recStack, graph):
            visited[v] = True
            recStack[v] = True
            for neighbour in graph[v]:
                if visited[neighbour] is False:
                    if check_cycle(neighbour, visited, recStack, graph) is \
                            True:
                        return True
                elif recStack[neighbour] is True:
                    return True
            recStack[v] = False
            return False

        boms_done = [(self, {'qty': quantity, 'product': product,
                             'original_qty': quantity, 'parent_line': False})]
        lines_done = []
        V |= set([product.product_tmpl_id.id])

        bom_lines = [(bom_line, product, quantity, False) for bom_line in
                     self.bom_line_ids]
        for bom_line in self.bom_line_ids:
            V |= set([bom_line.product_id.product_tmpl_id.id])
            graph[product.product_tmpl_id.id].append(
                bom_line.product_id.product_tmpl_id.id)
        while bom_lines:
            current_line, current_product, current_qty, parent_line = \
                bom_lines[0]
            bom_lines = bom_lines[1:]

            if current_line._skip_bom_line(current_product):
                continue

            line_quantity = current_qty * current_line.product_qty
            bom = self._bom_find_prepare(
                product=current_line.product_id,
                picking_type=picking_type or self.picking_type_id,
                company_id=self.company_id.id)
            if bom.type == 'phantom':
                converted_line_quantity = \
                    current_line.product_uom_id._compute_quantity(
                        line_quantity / bom.product_qty, bom.product_uom_id)
                bom_lines = [(line, current_line.product_id,
                              converted_line_quantity, current_line) for
                             line in bom.bom_line_ids] + bom_lines
                for bom_line in bom.bom_line_ids:
                    graph[current_line.product_id.product_tmpl_id.id].append(
                        bom_line.product_id.product_tmpl_id.id)
                    if bom_line.product_id.product_tmpl_id.id in V and \
                            check_cycle(bom_line.product_id.product_tmpl_id.id,
                                        {key: False for key in V},
                                        {key: False for key in V}, graph):
                        raise UserError(_('Recursion error!  A product with '
                                          'a Bill of Material should not '
                                          'have itself in its BoM or child '
                                          'BoMs!'))
                    V |= set([bom_line.product_id.product_tmpl_id.id])
                boms_done.append(self._prepare_consume_line(
                    bom, converted_line_quantity, current_product, quantity,
                    current_line))
            else:
                # We round up here because the user expects that if he has
                # to consume a little more, the whole UOM unit
                # should be consumed.
                rounding = current_line.product_uom_id.rounding
                line_quantity = float_round(
                    line_quantity,
                    precision_rounding=rounding,
                    rounding_method='UP')
                lines_done.append(self._prepare_consume_line(
                    current_line, line_quantity, current_product, quantity,
                    parent_line))

        return boms_done, lines_done
