# Copyright 2024 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade


logger = logging.getLogger(__name__)

related_fields = [
    ("company_id", "Company"),
]

related_models = [
    "mrp_workorder",
    "mrp_bom_line",
]

relations = {
    "mrp_workorder": {
        "field_name": "production_id",
        "model_name": "mrp_production",
    },
    "mrp_bom_line": {
        "field_name": "bom_id",
        "model_name": "mrp_bom",
    },
}


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.
    """
    store_related_fields(cr, related_models, related_fields, relations)


def store_related_fields(cr, model_list, field_list, relations):
    for model_name in model_list:
        for field_name, field_description in field_list:
            if not openupgrade.column_exists(
                    cr,
                    model_name,
                    field_name
            ):
                logger.info('Creating field %(field_name)s on %(model_name)s' % {
                    "field_name": field_name,
                    "model_name": model_name,
                })
                openupgrade.logged_query(
                    cr,
                    """
                    ALTER TABLE %(model_name)s ADD COLUMN %(field_name)s integer;
                    COMMENT ON COLUMN %(model_name)s.%(field_name)s IS
                    '%(field_description)s';
                    """ %
                    {
                        "model_name": model_name,
                        "field_name": field_name,
                        "field_description": field_description,
                    })
            logger.info('Update %(field_name)s values on %(model_name)s' % {
                    "field_name": field_name,
                    "model_name": model_name,
                })
            relation_dict = relations.get(model_name)
            if relation_dict:
                openupgrade.logged_query(
                    cr,
                    """
                    UPDATE %(model_name)s m
                    SET %(field_name)s = p.%(field_name)s
                    FROM %(relation_model)s p
                    WHERE m.%(relation_field)s = p.id 
                    AND p.%(field_name)s IS NOT NULL;
                    """ %
                    {
                        "model_name": model_name,
                        "field_name": field_name,
                        "relation_model": relation_dict.get("model_name"),
                        "relation_field": relation_dict.get("field_name"),
                    }
                )
