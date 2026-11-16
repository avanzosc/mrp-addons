.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=========================
Quality Control Usability
=========================

This module extends the functionality of quality_control_oca to improve the usability and management of quality control tests and inspections.

Features
--------

**Quality Inspection Duplication**

    - Allows quality inspections to be duplicated while preserving the assigned quality test.

    - Automatically generates the inspection lines based on the questions configured in the assigned test.

    - Assigns a custom name to duplicated inspections by appending an incremental suffix (-01, -02, etc.) to the original inspection name.

    - Prevents duplicated inspections from consuming numbers from the standard quality inspection sequence.

    -Sets duplicated inspections to draft state.

**Quality Inspection Management**

    - Makes the Correct field editable directly from the quality inspection form, allowing users to manually modify the inspection result.

**Quality Test Management**

    - Adds a new Product Templates tab to the quality test form.

    - Displays and allows management of the product template triggers associated with each quality test.

    - Allows users to configure the product templates and trigger types directly from the quality test form.

Usage
-----

**Duplicate a Quality Inspection**

1. Navigate to Quality Control > Inspections.
2. Open an existing quality inspection.
3. Select Action > Duplicate.
4. A new inspection will be created in draft state, retaining the original test and automatically generating its inspection lines.
5. The new inspection will receive the original inspection name with an incremental suffix, without affecting the standard inspection numbering sequence.

**Manage Quality Test Product Triggers**

1. Navigate to Quality Control > Tests.
2. Open a quality test.
3. Go to the Product Templates tab.
4. Add or modify the product templates and their associated trigger types.

**Modify an Inspection Result**

1. Navigate to Quality Control > Inspections.
2. Open a quality inspection.
3. Modify the Correct field directly from the inspection form.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted
it first, help us smash it by providing detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Contributors
------------

* Berezi Amubieta <bereziamubieta@avanzosc.es>
* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
