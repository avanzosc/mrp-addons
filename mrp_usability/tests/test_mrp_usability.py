# Copyright 2020 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestMrpUsability(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpUsability, cls).setUpClass()
        cls.production_obj = cls.env['mrp.production']

    def test_mrp_usability(self):
        productions = self.production_obj.search([])
        for production in productions:
            self.assertEquals(
                production.moves_to_consume_count,
                len(production.move_raw_ids))
