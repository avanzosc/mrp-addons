/* @odoo-module */

import {MoOverview} from "@mrp/components/mo_overview/mrp_mo_overview";
import {patch} from "@web/core/utils/patch";

patch(MoOverview.prototype, {
  async getManufacturingData() {
    await super.getManufacturingData(...arguments);

    const canShowCosts = Boolean(this.state.data?.show_costs);

    // Si el usuario no tiene permiso,
    // ocultamos todas las columnas relacionadas con costes.
    if (!canShowCosts) {
      this.state.showOptions.moCosts = false;
      this.state.showOptions.realCosts = false;
      this.state.showOptions.bomCosts = false;
      this.state.showOptions.unitCosts = false;
    }
  },

  onChangeDisplay(displayInfo) {
    const canShowCosts = Boolean(this.state.data?.show_costs);

    // Evitamos que el usuario pueda activar los costes
    // desde el desplegable "Mostrar en pantalla".
    const costOptions = ["moCosts", "realCosts", "bomCosts", "unitCosts"];

    if (!canShowCosts && costOptions.includes(displayInfo)) {
      return;
    }

    return super.onChangeDisplay(...arguments);
  },
});
