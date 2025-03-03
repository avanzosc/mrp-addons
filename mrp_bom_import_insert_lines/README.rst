.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://opensource.org/licenses/LGPL-3.0
   :alt: License: LGPL-3

===========================
MRP BoM Import Insert Lines
===========================

Overview
========

The **MRP BoM Import Insert Lines** module extends the functionality of the `mrp.bom.import` model to allow inserting new lines into existing Bills of Materials (BoMs) when importing BoM data.

Instead of requiring the creation of new BoMs, this module searches for existing BoMs for the same parent product and adds the imported lines to those BoMs, if they exist.

Features
========

- Extends the `action_insert_lines` method of `mrp.bom.import`.
- Processes only valid (`state="pass"`) import lines.
- Groups lines by parent product (BoM parent product).
- Searches for existing BoMs for each parent product.
- Adds the new lines to the existing BoM if found.
- Skips products without existing BoMs, logging a message for traceability.
- Updates the imported line with the corresponding `bom_id` and `bom_line_id`.

Usage
=====

1. **Prepare the BoM Import Data**:

    - Make sure the import lines have a `bom_product_id` (parent product).

2. **Run the Import Process**:

    - Go to *Manufacturing > Configuration > BoM Imports*.

    - Open an existing `mrp.bom.import` record.

    - Click on the new **Insert Lines** button (or trigger `action_insert_lines`).

3. **Results**:

    - If a BoM exists for the parent product, the imported lines are added to it.

    - If no BoM exists for the parent product, a log message is recorded, but no error is raised.

Configuration
=============

No additional configuration is required to use this module.

Testing
=======

1. Create a product with a Bill of Materials.
2. Prepare an import file with new BoM lines for that product.
3. Import the file using the standard BoM import process.
4. Trigger the **Insert Lines** action.
5. Verify that the existing BoM is updated with the new lines.

Bug Tracker
===========

Bugs and issues can be reported on the GitHub repository: 
`GitHub Issues <https://github.com/avanzosc/mrp-addons/issues>`_.

Credits
=======

Contributors
------------

* Ana Juaristi <anajuaristi@avanzosc.es>
* Unai Beristain <unaiberistain@avanzosc.es>

For further information, please contact the contributors.

License
=======

This project is licensed under the LGPL-3 License. 
For more details, see the LICENSE file or visit: 
<https://opensource.org/licenses/LGPL-3.0>.
