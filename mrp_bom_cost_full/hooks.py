def _post_install_mrp_bom_cost_full(env):
    cr = env.cr
    overhead = float(
        env["ir.config_parameter"].sudo().get_param("mrp_bom_overhead", default=15)
    )
    cr.execute(
        """
         UPDATE mrp_bom
         SET overhead = %s
    """,
        (overhead,),
    )
    cr.execute(
        """
         UPDATE mrp_bom_line
         SET overhead = %s
    """,
        (overhead,),
    )
    cr.execute(
        """
         UPDATE mrp_routing_workcenter
         SET overhead = %s
    """,
        (overhead,),
    )
    lines = env["mrp.bom.line"].search([])
    for line in lines:
        line.material_cost = line.product_id.standard_price
    operations = env["mrp.routing.workcenter"].search([])
    for op in operations:
        op.hour_cost = op.workcenter_id.costs_hour if op.workcenter_id else 0
    cond = [("time_cycle", "=", 0), ("time_cycle_manual", "!=", 0)]
    operations = env["mrp.routing.workcenter"].search(cond)
    for op in operations:
        op.time_cycle = op.time_cycle_manual
