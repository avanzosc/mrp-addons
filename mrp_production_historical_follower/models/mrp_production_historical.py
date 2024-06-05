# -*- coding: utf-8 -*-
# Copyright 2014 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class MrpProductionHistorical(models.Model):
    _inherit = "mrp.production.historical"

    @api.model
    def create(self, vals):
        historical = super(MrpProductionHistorical, self).create(vals)
        if "from_bom_activated" in self.env.context:
            historical._send_ldm2_email()
        if "bomline_historical_update" in self.env.context:
            historical._send_ldm2_email()
        if "bomline_historical_noupdate" in self.env.context:
            historical._send_ldm_email()
        if "scrap_history" in self.env.context:
            historical._send_scraped_email()
        if "add_historical" in self.env.context:
            historical._send_add_email()
        return historical

    def _send_scraped_email(self):
        template = self.env.ref(
            "mrp_production_historical_follower.mrp_production_historical_scraped",
            False)
        if template:
            for partner in self.production_id.mrp_production_follower_ids:
                self.send_email_to_follower(template, partner)

    def _send_add_email(self):
        template = self.env.ref(
            "mrp_production_historical_follower.mrp_production_historical_add",
            False)
        if template:
            for partner in self.production_id.mrp_production_follower_ids:
                self.send_email_to_follower(template, partner)

    def _send_ldm_email(self):
        template = self.env.ref(
            "mrp_production_historical_follower.mrp_production_histo_bom1",
            False)
        if template:
            for partner in self.production_id.mrp_production_follower_ids:
                self.send_email_to_follower(template, partner)

    def _send_ldm2_email(self):
        template = self.env.ref(
            "mrp_production_historical_follower.mrp_production_histo_bom2",
            False)
        if template:
            for partner in self.production_id.mrp_production_follower_ids:
                self.send_email_to_follower(template, partner)

    def send_email_to_follower(self, template, partner):
        wizard = self.env["mail.compose.message"].with_context(
            default_composition_mode="mass_mail",
            default_template_id=template and template.id or False,
            default_use_template=True,
            active_id=self.id,
            active_ids=self.ids,
            active_model="mrp.production.historical",
            default_model="mrp.production.historical",
            default_res_id=self.id,
            force_send=True
        ).create({"subject": template.subject,
                  "body": template.body_html,
                  "partner_ids": [(6, 0, partner.ids)],
                  "lang": partner.lang})
        values = wizard._onchange_template_id(
            template.id, "mass_mail", "mrp.production.historical",
            self.id)["value"]
        wizard.write(values)
        wizard.action_send_mail()
