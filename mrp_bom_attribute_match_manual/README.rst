.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
MRP BoM Attribute Match Manual
===================================

This module makes the ``Match on Attributes`` field editable on BoM component
lines provided by ``mrp_bom_attribute_match``.

It also adds a ``Component Match Attribute`` field to map a parent product
attribute to a different component attribute. For example, a skateboard can use
``M2`` as the parent attribute while the component template uses ``Color``.
When manufacturing a variant with ``M2 = Red``, the module searches for the
component variant with ``Color = Red``.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/mrp-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported.

Credits
=======

Authors
-------

* AvanzOSC

Contributors
------------

* Ane Gurruchaga <aneavanzosc@gmail.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
