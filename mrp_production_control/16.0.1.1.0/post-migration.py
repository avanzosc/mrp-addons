import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    query = """
        UPDATE mrp_production_control
        set manual_date = create_date
    """
    env.cr.execute(query)
