.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://opensource.org/licenses/LGPL-3.0
   :alt: License: LGPL-3

============================
MRP Production Customer Code
============================

Overview
========

The **MRP Production Customer Code** module adds a "Customer Code" field to the manufacturing orders. This field is automatically filled based on the product's customer-specific information, allowing for a more tailored approach to managing customer data in manufacturing.

Features
========

- **Customer Code Field**:

  - Displays the customer-specific code on the production order form.

- **Automatic Population**:

  - The "Customer Code" field is automatically filled by searching for the relevant customer code based on the product and partner.

- **Seamless Integration**:

  - The module integrates with the `product.customerinfo` model to fetch the appropriate customer code.

Usage
=====

1. **Install the Module**:
   - Install the **MRP Production Customer Code** module from the Apps menu.

2. **View Customer Code**:
   - Open a manufacturing order.
   - The "Customer Code" field will automatically populate with the code associated with the product and customer.

Configuration
=============

No additional configuration is required. The module works automatically once installed.

Testing
=======

1. Create a manufacturing order with a product and customer.
2. Verify that the "Customer Code" field is populated based on the customer-specific data.

Bug Tracker
===========

If you encounter any issues, please report them on the GitHub repository at `GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_.

Credits
=======

Contributors
------------

* Ana Juaristi <anajuaristi@avanzosc.es>
* Unai Beristain <unaiberistain@avanzosc.es>

For specific questions or support, please contact the contributors.

License
=======

This project is licensed under the LGPL-3 License. For more details, refer to the LICENSE file or visit <https://opensource.org/licenses/LGPL-3.0>.
