"""One-time migration of operations/workorders without a historical task."""

import logging
from collections import defaultdict

from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
BATCH_SIZE = 500
MODULE = "mrp_workcenter_section"


def _section_map(env, section_map):
    """Resolve historical workcenter -> section without guessing duplicates."""
    if section_map is not None:
        return dict(section_map)

    sections = env["mrp.workcenter.section"].sudo().search([])
    by_name = defaultdict(list)
    for section in sections:
        by_name[section.name].append(section.id)

    result = {}
    tasks = env["mrp.capacidad.tarea"].sudo().search([])
    for task in tasks:
        old = task.workcenter_id
        if not old:
            continue
        candidates = by_name.get(old.name, [])
        if len(candidates) > 1:
            raise UserError(
                _("Varias secciones tienen el nombre del centro original %s.")
                % old.name
            )
        if candidates:
            result[old.id] = candidates[0]
    return result


def _generic_center(env, old_id, section_id, dry_run):
    """Resolve a generic center via a stable XML ID, creating only if needed."""
    Workcenter = env["mrp.workcenter"].sudo().with_context(active_test=False)
    Data = env["ir.model.data"].sudo()
    xml_name = f"generic_workcenter_{old_id}"
    data = Data.search([("module", "=", MODULE), ("name", "=", xml_name)], limit=2)
    if len(data) > 1:
        raise UserError(_("XML ID duplicado para el centro original %s.") % old_id)
    if data:
        if data.model != "mrp.workcenter":
            raise UserError(_("El XML ID %s pertenece a otro modelo.") % xml_name)
        center = Workcenter.browse(data.res_id).exists()
        if not center or center.section_id.id != section_id:
            raise UserError(
                _("El centro genérico %s no existe o tiene otra sección.") % xml_name
            )
        return center.id, False

    section = env["mrp.workcenter.section"].sudo().browse(section_id)
    old = Workcenter.browse(old_id)
    if not old.exists() or not section.exists():
        raise UserError(_("Centro original o sección inexistente: %s.") % old_id)

    name = f"Varios - {section.name}"
    collision = Workcenter.search(
        [("name", "=", name), ("section_id", "=", section_id)], limit=1
    )
    if collision:
        raise UserError(
            _("Ya existe '%s' sin XML ID de migración. Revisar manualmente.") % name
        )
    if dry_run:
        return None, True

    center = Workcenter.create(
        {
            "name": name,
            "section_id": section_id,
            "company_id": old.company_id.id,
            "resource_calendar_id": old.resource_calendar_id.id,
            "default_capacity": old.default_capacity,
            "sequence": old.sequence,
        }
    )
    Data.create(
        {
            "module": MODULE,
            "name": xml_name,
            "model": "mrp.workcenter",
            "res_id": center.id,
            "noupdate": True,
        }
    )
    return center.id, True


def _update_batches(env, model, ids, center_id, dry_run):
    """SQL-write only workcenter_id, notifying ORM about dependencies."""
    if dry_run or not ids:
        return 0
    Model = env[model].sudo()
    Model.flush_model(["workcenter_id"])
    table = {
        "mrp.routing.workcenter": "mrp_routing_workcenter",
        "mrp.workorder": "mrp_workorder",
    }[model]
    updated = 0
    for pos in range(0, len(ids), BATCH_SIZE):
        batch = ids[pos : pos + BATCH_SIZE]
        # Table names are static from the local whitelist, never user input.
        env.cr.execute(
            f"UPDATE {table} SET workcenter_id = %s WHERE id = ANY(%s) "
            "AND workcenter_id IS DISTINCT FROM %s RETURNING id",
            (center_id, batch, center_id),
        )
        changed = [row[0] for row in env.cr.fetchall()]
        if not changed:
            continue
        records = Model.browse(changed)
        records.invalidate_recordset(["workcenter_id"])
        records.modified(["workcenter_id"])
        env.flush_all()
        env.invalidate_all(flush=False)
        updated += len(changed)
    return updated


def migrate_generic_workcenters(env, section_map=None, dry_run=True):
    """Map no-history operations and no-task workorders to generic centers.

    Never reassign operations with any non-null historical task, even when
    historical workorders disagree with the operation's original workcenter.
    Exclude original workcenters without an unambiguous section (Varistores).
    No commit is performed; caller controls the transaction.
    """
    mapping = _section_map(env, section_map)
    if not mapping:
        raise UserError(_("No se pudieron identificar secciones originales."))

    Routing = env["mrp.routing.workcenter"].sudo()
    Workorder = env["mrp.workorder"].sudo()
    Routing.flush_model(["workcenter_id", "tarea"])
    Workorder.flush_model(["workcenter_id", "tarea_id", "operation_id"])

    # Only no-history operations. The NOT EXISTS also protects the 143
    # operations with an identifiable but historically inconsistent task.
    env.cr.execute(
        """
        SELECT r.id, r.workcenter_id
          FROM mrp_routing_workcenter r
         WHERE r.tarea IS NULL
           AND NOT EXISTS (
               SELECT 1 FROM mrp_workorder w
                WHERE w.operation_id = r.id AND w.tarea_id IS NOT NULL
           )
        """
    )
    operations = defaultdict(list)
    excluded_operations = 0
    for rec_id, old_id in env.cr.fetchall():
        if old_id in mapping:
            operations[old_id].append(rec_id)
        else:
            excluded_operations += 1

    # Only workorders without task whose current center is still an original
    # workcenter with a known section. Exclude rows already migrated, naturally.
    env.cr.execute(
        """
        SELECT id, workcenter_id
          FROM mrp_workorder
         WHERE tarea_id IS NULL
        """
    )
    workorders = defaultdict(list)
    excluded_workorders = 0
    for rec_id, old_id in env.cr.fetchall():
        if old_id in mapping:
            workorders[old_id].append(rec_id)
        else:
            excluded_workorders += 1

    needed_old_ids = sorted(set(operations) | set(workorders))
    counts = {
        "eligible_operations": sum(map(len, operations.values())),
        "eligible_workorders": sum(map(len, workorders.values())),
        "excluded_operations": excluded_operations,
        "excluded_workorders": excluded_workorders,
        "centers_to_create": 0,
        "centers_reused": 0,
        "updated_operations": 0,
        "updated_workorders": 0,
    }
    centers = {}
    for old_id in needed_old_ids:
        center_id, is_new = _generic_center(env, old_id, mapping[old_id], dry_run)
        centers[old_id] = center_id
        counts["centers_to_create" if is_new else "centers_reused"] += 1
    _logger.info("Generic migration (dry_run=%s): %s", dry_run, counts)
    if dry_run:
        return counts

    for old_id in needed_old_ids:
        target = centers[old_id]
        counts["updated_operations"] += _update_batches(
            env, "mrp.routing.workcenter", operations[old_id], target, False
        )
        counts["updated_workorders"] += _update_batches(
            env, "mrp.workorder", workorders[old_id], target, False
        )

    Routing.flush_model(["workcenter_id", "section_id"])
    Workorder.flush_model(["workcenter_id", "section_id"])
    for table, field in (
        ("mrp_routing_workcenter", "tarea"),
        ("mrp_workorder", "tarea_id"),
    ):
        env.cr.execute(
            f"""
            SELECT COUNT(*) FROM {table} r
            JOIN mrp_workcenter wc ON wc.id = r.workcenter_id
            WHERE r.{field} IS NULL AND wc.section_id IS NOT NULL
              AND r.section_id IS DISTINCT FROM wc.section_id
            """
        )
        wrong = env.cr.fetchone()[0]
        if wrong:
            raise UserError(
                _("Hay %(count)s secciones incorrectas en %(table)s.")
                % {"count": wrong, "table": table}
            )
    _logger.info("Generic migration complete: %s", counts)
    return counts
