.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: https://opensource.org/licenses/AGPL-3.0
   :alt: License: AGPL-3

=====================================
MRP Workorder Components Availability
=====================================

This module extends the **Manufacturing Workorder** (`mrp.workorder`) model to display the **component availability** and **readiness status** of the parent Manufacturing Order (MO) directly on the workorder views.  

- **MO Component Status**  
  Shows the latest component availability status inherited from the parent MO.

- **MO Components Availability State**  
  Displays whether components are *Available*, *Expected*, or *Late*.

- **MO Readiness**  
  Indicates the material readiness of the parent MO based on the Bill of Materials (BoM) configuration:  
  - **Ready**: All required materials are available.  
  - **Waiting**: Materials are not yet available.  
  - **Waiting Another Operation**: Materials are dependent on another operation.  

- **UI Enhancements**  
  Adds color-coded decorations to the workorder tree view to visually highlight the availability and readiness states:
  - **Green (Success)**: Ready to start production.  
  - **Orange (Warning)**: Components expected or partially available.  
  - **Red (Danger)**: Components are late or unavailable.  

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

* Ana Juaristi <anajuaristi@avanzosc.es>

* Lucía Echeverría <luciaecheverria@avanzosc.es>

For specific questions regarding this module, please contact the contributors. For support, please use the official issue tracker.

License
=======

This project is licensed under the AGPL-3 License. For more details, refer to the LICENSE file or visit <https://opensource.org/licenses/AGPL-3.0>.

