# Copyright 2022 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

def post_init_hook(cr, registry):
    cr.execute("""
        UPDATE mrp_bom_line b
           SET product_tmpl_id = (
            SELECT product_tmpl_id
              FROM product_product p
             WHERE p.id = b.product_id)
         WHERE product_tmpl_id IS Null
    """)
