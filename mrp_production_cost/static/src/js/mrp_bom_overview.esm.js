/* @odoo-module */

import {BomOverviewComponent} from "@mrp/components/bom_overview/mrp_bom_overview";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewComponent.prototype, {
  async getBomData() {
    const bomData = await super.getBomData(...arguments);

    const canShowCosts = Boolean(bomData.lines?.show_costs);

    // El usuario no tiene permiso:
    // desactivamos completamente la opción estándar de costes.
    if (!canShowCosts) {
      this.state.showOptions.costs = false;
    }

    return bomData;
  },

  onChangeDisplay(displayInfo) {
    // Evitamos que un usuario sin permisos pueda volver
    // a activar "Costs" desde el menú Display.
    if (displayInfo === "costs" && !this.state.bomData?.show_costs) {
      return;
    }

    return super.onChangeDisplay(...arguments);
  },
});
