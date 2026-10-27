.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0.html
   :alt: License: AGPL-3

====================================
Quality Inspection Sale Confirmation
====================================

Overview
--------

The **Quality Inspection Sale Confirmation** module automatically creates quality inspections when a sales order is confirmed and its corresponding delivery order is generated.

This allows quality inspections to be performed before validating the delivery order, rather than waiting until the stock picking reaches the Done state.

Features
--------

- **Automatic Quality Inspection Creation**: Generates quality inspections when a sales order is confirmed and its delivery order is created.
- **Integration with Quality Control**: Uses the existing quality control triggers and inspection rules configured for products.
- **Duplicate Inspection Prevention**: Prevents duplicate quality inspections from being created when the delivery order is validated.

Usage
-----

1. **Install the Module**:

   - Install the module via Odoo's Apps interface.

2. **Confirm a Sales Order**:

   - Navigate to **Sales > Orders > Quotations**.
   - Create or open a quotation containing products with configured quality control rules.
   - Confirm the quotation to generate the sales order and its corresponding delivery order.

3. **View Quality Inspections**:

   - Open the delivery order associated with the confirmed sales order.
   - Verify that the corresponding quality inspections have been automatically created.
   - The inspections are available before the delivery order is validated.

Configuration
-------------

No additional configuration is required. The module uses the existing quality control triggers and inspection rules configured in Odoo.

Testing
-------

Test the following scenarios:

- **Automatic Quality Inspection Creation**:

  - Create a quotation containing products with configured quality control rules.
  - Confirm the quotation.
  - Verify that the delivery order is generated and the corresponding quality inspections are automatically created.

- **Quality Inspections Before Delivery Validation**:

  - Open the delivery order generated from the confirmed sales order.
  - Verify that the quality inspections are available before the delivery order reaches the Done state.

- **Duplicate Inspection Prevention**:

  - Confirm a sales order and verify that the corresponding quality inspections are created.
  - Validate the associated delivery order.
  - Verify that no duplicate quality inspections are generated.

Bug Tracker
===========

If you encounter any issues, please report them on the GitHub repository at `GitHub Issues <https://github.com/avanzosc/mrp-addons/issues>`_.

Credits
=======

Contributors
------------

* Berezi Amubieta <bereziamubieta@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>

For module-specific questions, please contact the contributors directly. Support requests should be made through the official channels.

License
=======

This project is licensed under the AGPL-3 License. For more details, please refer to the LICENSE file or visit <https://www.gnu.org/licenses/agpl-3.0.html>.
