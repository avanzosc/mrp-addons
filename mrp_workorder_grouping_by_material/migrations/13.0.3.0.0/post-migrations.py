# Copyright 2023 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    nests = env["mrp.workorder.nest"].search(
        [
            ("state", "=", "blocked"),
        ]
    )
    for nest in nests:
        nest_line_states = nest.mapped("nested_line_ids.state")
        if all([state == "cancel" for state in nest_line_states]):
            nest.sudo().write({"state": "cancel"})
        elif all([state in ("done", "cancel") for state in nest_line_states]):
            nest.sudo().write(
                {
                    "state": "done",
                }
            )
