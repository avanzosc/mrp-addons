# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Quality control claim",
    "version": "14.0.1.0.0",
    "author": "OdooMRP team," "AvanzOSC," "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "https://github.com/avanzosc/mrp-addons",
    "license": "AGPL-3",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Daniel Campos <danielcampos@avanzosc.es>",
    ],
    "category": "Quality control",
    "depends": [
        "quality_control_oca",
        "crm_claim",
    ],
    "data": [
        "views/qc_test_view.xml",
        "views/qc_inspection_view.xml",
    ],
    "installable": True,
}
