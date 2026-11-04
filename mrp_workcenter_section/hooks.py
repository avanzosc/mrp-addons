import logging

from odoo import _
from odoo.exceptions import UserError

from .generic_migration import migrate_generic_workcenters
from .routing_migration import migrate_routing_operations

_logger = logging.getLogger(__name__)

BATCH_SIZE = 500


def _validate_tareas(tareas):
    for tarea in tareas:
        if not tarea.name or not tarea.name.strip():
            raise UserError(_("La tarea %s no tiene nombre.") % tarea.id)

        if not tarea.workcenter_id:
            raise UserError(_("La tarea %s no tiene centro original.") % tarea.id)


def post_init_hook(env):
    _logger.info("Iniciando migración de centros y tareas")

    Workcenter = env["mrp.workcenter"].sudo()
    Section = env["mrp.workcenter.section"].sudo()
    Tarea = env["mrp.capacidad.tarea"].sudo()
    Workorder = env["mrp.workorder"].sudo()

    # --------------------------------------------------
    # 1. Evitar una migración duplicada
    # --------------------------------------------------
    if Section.search_count([]):
        raise UserError(
            _(
                "Ya existen secciones de producción. "
                "Revisar antes de ejecutar la migración."
            )
        )

    # --------------------------------------------------
    # 2. Recuperar centros originales activos
    # --------------------------------------------------
    old_workcenters = Workcenter.search(
        [
            ("active", "=", True),
        ]
    )

    if not old_workcenters:
        raise UserError(_("No se encontraron centros de trabajo activos."))

    old_workcenter_ids = old_workcenters.ids

    _logger.info(
        "Centros originales activos: %s",
        len(old_workcenter_ids),
    )

    # --------------------------------------------------
    # 3. Recuperar y validar tareas
    # --------------------------------------------------
    tareas = Tarea.search(
        [
            ("workcenter_id", "in", old_workcenter_ids),
        ]
    )

    if not tareas:
        raise UserError(_("No se encontraron tareas para migrar."))

    _validate_tareas(tareas)
    tarea_ids = tareas.ids

    _logger.info(
        "Tareas validadas para migración: %s",
        len(tarea_ids),
    )

    # --------------------------------------------------
    # 4. Analizar órdenes de trabajo
    # --------------------------------------------------
    total_workorders = Workorder.search_count(
        [
            ("tarea_id", "in", tarea_ids),
        ]
    )

    total_historicas = Workorder.search_count(
        [
            ("tarea_id", "in", tarea_ids),
            ("state", "in", ["done", "cancel"]),
        ]
    )

    total_en_progreso = Workorder.search_count(
        [
            ("tarea_id", "in", tarea_ids),
            ("state", "=", "progress"),
        ]
    )

    _logger.info(
        "Órdenes con tarea migrable: %s",
        total_workorders,
    )
    _logger.info(
        "Órdenes finalizadas/canceladas: %s",
        total_historicas,
    )
    _logger.info(
        "Órdenes en progreso: %s",
        total_en_progreso,
    )

    # --------------------------------------------------
    # 5. Crear secciones
    # --------------------------------------------------
    section_map = {}

    for workcenter in old_workcenters:
        section = Section.create(
            {
                "name": workcenter.name,
            }
        )

        section_map[workcenter.id] = section.id

    _logger.info(
        "Secciones creadas: %s",
        len(section_map),
    )

    # --------------------------------------------------
    # 6. Crear centros a partir de las tareas
    # --------------------------------------------------
    task_map = {}

    for tarea in tareas:
        old_workcenter = tarea.workcenter_id

        new_workcenter = Workcenter.create(
            {
                "name": tarea.name,
                "section_id": section_map[old_workcenter.id],
                "company_id": old_workcenter.company_id.id,
                "resource_calendar_id": (old_workcenter.resource_calendar_id.id),
                "default_capacity": (old_workcenter.default_capacity),
                "sequence": old_workcenter.sequence,
            }
        )

        task_map[tarea.id] = new_workcenter.id

    _logger.info(
        "Centros nuevos creados: %s",
        len(task_map),
    )

    # --------------------------------------------------
    # 7. Actualizar órdenes en lotes
    # --------------------------------------------------
    total_actualizadas = 0
    total_lotes = 0

    Workorder.flush_model(
        [
            "workcenter_id",
            "tarea_id",
        ]
    )

    for tarea_id, new_workcenter_id in task_map.items():
        last_id = 0
        actualizadas_tarea = 0

        while True:
            # Seleccionar hasta 500 órdenes de esta tarea,
            # sin cargar todas sus IDs en memoria.
            #
            # El cursor last_id permite avanzar por la
            # tabla sin OFFSET.

            env.cr.execute(
                """
                SELECT id
                FROM mrp_workorder
                WHERE tarea_id = %s
                  AND id > %s
                  AND workcenter_id IS DISTINCT FROM %s
                ORDER BY id
                LIMIT %s
                """,
                (
                    tarea_id,
                    last_id,
                    new_workcenter_id,
                    BATCH_SIZE,
                ),
            )

            batch_ids = [row[0] for row in env.cr.fetchall()]

            if not batch_ids:
                break

            last_id = batch_ids[-1]

            # Actualizar únicamente este lote.
            env.cr.execute(
                """
                UPDATE mrp_workorder
                SET workcenter_id = %s
                WHERE id = ANY(%s)
                RETURNING id
                """,
                (
                    new_workcenter_id,
                    batch_ids,
                ),
            )

            updated_ids = [row[0] for row in env.cr.fetchall()]

            if not updated_ids:
                continue

            updated_workorders = Workorder.browse(updated_ids)

            # Sincronizar la caché con el SQL ejecutado.
            updated_workorders.invalidate_recordset(
                [
                    "workcenter_id",
                ]
            )

            # Notificar las modificaciones al ORM.
            updated_workorders.modified(
                [
                    "workcenter_id",
                ]
            )

            # MUY IMPORTANTE:
            # Resolver las recomputaciones pendientes
            # antes de procesar el siguiente lote.
            #
            # No hace COMMIT: todo sigue dentro
            # de la transacción de instalación.
            env.flush_all()

            # Liberar las referencias de caché que
            # ya no necesitamos.
            env.invalidate_all(flush=False)

            actualizadas_tarea += len(updated_ids)
            total_actualizadas += len(updated_ids)
            total_lotes += 1

            if total_lotes % 10 == 0:
                _logger.info(
                    "Migración de órdenes: %s actualizadas en %s lotes",
                    total_actualizadas,
                    total_lotes,
                )

        _logger.info(
            "Tarea %s: %s órdenes actualizadas",
            tarea_id,
            actualizadas_tarea,
        )

    _logger.info(
        "Órdenes de trabajo actualizadas: %s",
        total_actualizadas,
    )

    # --------------------------------------------------
    # 8. Validar órdenes y secciones
    # --------------------------------------------------
    Workorder.flush_model(
        [
            "workcenter_id",
            "section_id",
            "tarea_id",
        ]
    )

    total_pendientes = 0
    total_secciones_incorrectas = 0

    for tarea_id, new_workcenter_id in task_map.items():
        pendientes = Workorder.search_count(
            [
                ("tarea_id", "=", tarea_id),
                ("workcenter_id", "!=", new_workcenter_id),
            ]
        )

        total_pendientes += pendientes

        new_section_id = Workcenter.browse(new_workcenter_id).section_id.id

        secciones_incorrectas = Workorder.search_count(
            [
                ("tarea_id", "=", tarea_id),
                ("section_id", "!=", new_section_id),
            ]
        )

        total_secciones_incorrectas += secciones_incorrectas

    if total_pendientes:
        raise UserError(
            _("Quedan %s órdenes sin migrar correctamente.") % total_pendientes
        )

    if total_secciones_incorrectas:
        raise UserError(
            _("Quedan %s órdenes con sección incorrecta.") % total_secciones_incorrectas
        )

    _logger.info("Validación de órdenes y secciones completada.")

    # Migrar operaciones de las listas de materiales
    routing_result = migrate_routing_operations(
        env,
        task_map=task_map,
        dry_run=False,
    )

    _logger.info(
        "Migración de operaciones: %s actualizadas",
        routing_result["updated"],
    )

    # --------------------------------------------------
    # 9. Migrar registros sin tarea a centros genéricos
    # --------------------------------------------------
    generic_result = migrate_generic_workcenters(
        env,
        section_map=section_map,
        dry_run=False,
    )

    _logger.info(
        "Migración de centros genéricos: %s",
        generic_result,
    )

    # --------------------------------------------------
    # 9. Archivar centros originales
    # --------------------------------------------------
    Workcenter.browse(old_workcenter_ids).write(
        {
            "active": False,
        }
    )

    # Resolver cualquier recomputación pendiente
    # del archivado.
    env.flush_all()

    # --------------------------------------------------
    # 10. Resumen
    # --------------------------------------------------
    _logger.info("Migración finalizada correctamente.")

    _logger.info(
        "Secciones creadas: %s",
        len(section_map),
    )
    _logger.info(
        "Centros nuevos: %s",
        len(task_map),
    )
    _logger.info(
        "Órdenes actualizadas: %s",
        total_actualizadas,
    )
    _logger.info(
        "Lotes procesados: %s",
        total_lotes,
    )
    _logger.info(
        "Órdenes migrables sin cambios: %s",
        total_workorders - total_actualizadas,
    )
