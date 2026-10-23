"""One-time routing operation migration for mrp_workcenter_section."""

import logging
from collections import defaultdict

from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

BATCH_SIZE = 500


def _existing_task_map(env):
    """Return legacy task id -> newly created center id; never guess matches."""
    Task = env["mrp.capacidad.tarea"].sudo()
    Section = env["mrp.workcenter.section"].sudo()
    Center = env["mrp.workcenter"].sudo().with_context(active_test=False)
    mapping = {}
    for task in Task.search([]):
        old_center = task.workcenter_id
        if not old_center or not task.name:
            continue
        sections = Section.search([("name", "=", old_center.name)], limit=2)
        if len(sections) != 1:
            continue  # e.g. excluded Varistores
        centers = Center.search(
            [("name", "=", task.name), ("section_id", "=", sections.id)],
            limit=2,
        )
        if len(centers) != 1:
            raise UserError(
                _("No hay una correspondencia única para la tarea %s.") % task.id
            )
        mapping[task.id] = centers.id
    return mapping


def migrate_routing_operations(env, task_map=None, dry_run=True):
    """Migrate only routing operations whose historical task matches old center.

    Returns counts. Safe to rerun: already-migrated rows are skipped.
    Caller must commit explicitly for a standalone shell invocation.
    """
    Routing = env["mrp.routing.workcenter"].sudo()
    Task = env["mrp.capacidad.tarea"].sudo()
    Center = env["mrp.workcenter"].sudo().with_context(active_test=False)
    task_map = dict(task_map) if task_map is not None else _existing_task_map(env)
    if not task_map:
        raise UserError(
            _("No se encontraron tareas con centros nuevos identificables.")
        )

    # Workorders are the historical evidence. Include only operations with
    # exactly one non-null task across their historical workorders.
    env["mrp.workorder"].flush_model(["operation_id", "tarea_id"])
    Routing.flush_model(["workcenter_id", "tarea"])
    Task.flush_model(["workcenter_id"])
    env.cr.execute(
        """
        SELECT r.id, h.tarea_id, r.workcenter_id, r.tarea,
               t.workcenter_id AS old_task_center_id
          FROM mrp_routing_workcenter r
          JOIN (
                SELECT operation_id, MIN(tarea_id) AS tarea_id
                  FROM mrp_workorder
                 WHERE operation_id IS NOT NULL AND tarea_id IS NOT NULL
                 GROUP BY operation_id
                HAVING COUNT(DISTINCT tarea_id) = 1
               ) h ON h.operation_id = r.id
          JOIN mrp_capacidad_tarea t ON t.id = h.tarea_id
         ORDER BY h.tarea_id, r.id
        """
    )
    rows = env.cr.fetchall()
    grouped = defaultdict(list)
    counts = {
        "with_unique_history": len(rows),
        "eligible": 0,
        "already_migrated": 0,
        "different_legacy_center": 0,
        "without_new_center": 0,
        "historical_task_conflict": 0,
        "updated": 0,
    }
    for operation_id, task_id, current_center, current_task, old_center in rows:
        target_center = task_map.get(task_id)
        if target_center is None:
            counts["without_new_center"] += 1
            continue
        if current_task not in (None, task_id):
            counts["historical_task_conflict"] += 1
            continue
        if current_center == target_center and current_task == task_id:
            counts["already_migrated"] += 1
            continue
        if current_center not in (old_center, target_center):
            counts["different_legacy_center"] += 1
            continue
        # In the original state, the operation must belong to the very center
        # that owned the historical task. If already migrated, just fill tarea.
        if not Center.browse(target_center).section_id:
            counts["without_new_center"] += 1
            continue
        grouped[(task_id, target_center)].append(operation_id)
        counts["eligible"] += 1

    _logger.info("Routing migration (dry_run=%s): %s", dry_run, counts)
    if dry_run:
        return counts

    for (task_id, target_center), operation_ids in grouped.items():
        for i in range(0, len(operation_ids), BATCH_SIZE):
            batch = operation_ids[i : i + BATCH_SIZE]

            # Actualización directa para evitar que write() marque
            # las órdenes de fabricación como desactualizadas.
            env.cr.execute(
                """
                UPDATE mrp_routing_workcenter
                SET tarea = %s,
                    workcenter_id = %s
                WHERE id = ANY(%s)
                RETURNING id
                """,
                (task_id, target_center, batch),
            )

            updated_ids = [row[0] for row in env.cr.fetchall()]

            if not updated_ids:
                continue

            updated_operations = Routing.browse(updated_ids)

            # Sincronizar la caché ORM.
            updated_operations.invalidate_recordset(["tarea", "workcenter_id"])

            # Notificar las modificaciones para recalcular
            # los campos dependientes, especialmente section_id.
            updated_operations.modified(["tarea", "workcenter_id"])

            # Resolver las recomputaciones pendientes.
            env.flush_all()
            env.invalidate_all(flush=False)

            counts["updated"] += len(updated_ids)

            _logger.info(
                "Routing migration: %s / %s operations updated",
                counts["updated"],
                counts["eligible"],
            )

    Routing.flush_model(["tarea", "workcenter_id", "section_id"])
    # Validate exactly the updated rows, without querying a huge id list.
    # The workcenter's section must match the stored related section.
    env.cr.execute(
        """
        SELECT count(*)
          FROM mrp_routing_workcenter r
          JOIN mrp_workcenter wc ON wc.id = r.workcenter_id
         WHERE r.tarea IS NOT NULL
           AND r.section_id IS DISTINCT FROM wc.section_id
        """
    )
    mismatches = env.cr.fetchone()[0]
    if mismatches:
        raise UserError(
            _("Hay %s operaciones con sección relacionada incorrecta.") % mismatches
        )
    _logger.info("Routing migration complete: %s", counts)
    return counts
