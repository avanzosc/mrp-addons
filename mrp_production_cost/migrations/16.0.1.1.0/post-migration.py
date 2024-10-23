# Copyright 2024 Alfredo de la Fuente - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cond = [("state", "=", "done")]
    productions = env["mrp.production"].search(cond)
    for production in productions:
        production.update_prodution_cost()
