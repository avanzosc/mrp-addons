# Copyright 2021 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute("""
        DELETE FROM sale_line_attribute
        WHERE line_id IS NULL;
    """)
    cr.execute("""
        DELETE FROM sale_version_custom_line
        WHERE line_id IS NULL;
    """)
