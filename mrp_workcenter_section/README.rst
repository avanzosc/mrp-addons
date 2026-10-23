=======================
MRP Workcenter Sections
=======================
## Description

This module introduces production sections to improve the organization of manufacturing work centers in Odoo.

A production section represents a group of related work centers. Each work center can be assigned to a section, allowing manufacturing operations and work orders to be organized, searched, and grouped by section.

The module also provides a migration process for legacy manufacturing data, where production work centers represent sections and production tasks represent individual work centers.

## Features

- Create and manage production sections.
- Assign a production section to each work center.
- Display sections on work center, manufacturing operation, and work order views.
- Search and group work centers and manufacturing operations by section.
- Automatically determine the section of a manufacturing operation or work order from its assigned work center.
- Preserve references to legacy production tasks for historical traceability.

## Installation

The module can be installed on both new and existing Odoo databases.

When installed on a database containing legacy production tasks, a post-installation migration is performed to reorganize the manufacturing structure.

The migration:

1. Creates a production section for each eligible active legacy work center.
2. Creates new work centers from the legacy production tasks, assigning them to their corresponding sections.
3. Updates existing work orders to reference the new work centers.
4. Migrates manufacturing operations when their historical task can be identified reliably.
5. Creates generic work centers for eligible operations and work orders without an identifiable historical task.
6. Archives the original work centers after the migration.

The migration preserves historical task references and does not assign tasks when the available historical information is inconsistent.

Previously archived legacy work centers are excluded from the migration.

If no eligible legacy data is available, the module can be installed without performing the migration.

## Usage

### Production Sections

Navigate to **Manufacturing > Configuration > Sections** to create and manage production sections.

### Work Centers

Open a work center and assign it to a production section using the **Section** field.

Work centers can also be searched and grouped by section.

### Manufacturing Operations

The section associated with an operation is automatically obtained from its assigned work center.

Operations can be searched and grouped by section.

### Work Orders

The section associated with a work order is automatically obtained from its assigned work center.

This allows work orders to be organized according to their production sections without requiring manual section assignment.

## Technical Notes

The `section_id` field on manufacturing operations and work orders is a stored related field derived from `workcenter_id.section_id`.

Historical migration routines use batched SQL updates and notify the Odoo ORM to maintain the consistency of dependent fields.

The migration is executed during module installation and is not automatically repeated when the module is upgraded.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/avanzosc/mrp-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/avanzosc/mrp-addons/issues/new?body=module:%20mrp_production_cost%0Aversion:%2018.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* AvanzOSC

Contributors
~~~~~~~~~~~~

* Berezi Amubieta <bereziamubieta@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>

Maintainers
~~~~~~~~~~~

This module is part of the `avanzosc/mrp-addons <https://github.com/avanzosc/mrp-addons/tree/18.0/mrp_production_cost>`_ project on GitHub.

You are welcome to contribute.
