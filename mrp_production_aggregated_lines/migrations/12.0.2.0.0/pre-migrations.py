# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(
        cr,
        "product_product",
        "is_manufacturable"
    ):
        openupgrade.add_fields(
            env,
            [("is_manufacturable",
              "product.product",
              "product_product",
              "bool",
              False,
              "mrp_production_aggregated_lines")]
        )
        cr.execute("""
            ALTER TABLE product_product
            ADD COLUMN is_manufacturable bool;
        """)
    mrp_route = env.ref("mrp.route_warehouse0_manufacture")
    cr.execute(
        """
        UPDATE product_product
        SET is_manufacturable = True
        WHERE product_tmpl_id IN (
            SELECT product_id
            FROM stock_route_product
            WHERE route_id = %s)
        AND (id IN (
            SELECT product_id
            FROM mrp_bom)
        OR product_tmpl_id IN (
            SELECT product_tmpl_id
            FROM mrp_bom
            WHERE product_id IS NULL));
        """, (mrp_route.id, ))
