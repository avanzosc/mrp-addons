# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def post_init_hook(cr, registry):
    cr.execute("""
        UPDATE mrp_production
        SET active = True
        WHERE state != 'draft';
    """)
