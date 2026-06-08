.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Machine Manager in Manufacturing
================================

Machine Manager in Manufacturing is a companion module for **Machine Manager**
that connects your machinery records with Odoo's Manufacturing module. It
allows you to link each Work Center in your production floor directly to a
specific machine from your machine registry, bridging the gap between your
physical assets and your manufacturing operations.
 
This module requires both **Machine Manager** and the **Manufacturing** (mrp)
module to be installed. Once both are present, this module activates
automatically.
 
Features
========
 
Link a Machine to a Work Center
---------------------------------
 
A new **Machine** field is added to every Work Center record. This lets you
associate the physical machine that corresponds to each work Center, so your
production setup reflects the actual equipment on the shop floor.
 
Machine Column in Work Center List
------------------------------------
 
In the Work Center list view, a new optional column **Machine** is available.
When enabled, it shows the linked machine for each work Center at a glance,
without needing to open individual records.
 
Search Work Centers by Machine
--------------------------------
 
The Work Center search view includes a new **Machine** filter. You can search
for work Centers by the name of the machine linked to them, making it easy to
find which production station uses a specific piece of equipment.
 
Configuration
=============
 
No additional configuration is required. Once the module is installed:
 
1. Go to **Manufacturing → Configuration → Work Centers** and open any
   work Center.
 
2. Use the **Machine** field to link it to a machine from your Machine
   Manager registry.
 
3. Optionally enable the **Machine** column in the work Center list view
   using the column selector on the right side of the list header.

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
* Daniel Campos <danielcampos@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciobaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>
