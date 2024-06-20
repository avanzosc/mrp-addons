from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    task_ids = fields.One2many(
        "project.task", "mrp_production_id", string="Related Tasks"
    )

    def action_view_related_tasks(self):
        action = self.env.ref("project.action_view_task").read()[0]
        action["domain"] = [("id", "in", self.task_ids.ids)]
        action["context"] = {
            "default_project_id": self.project_id.id
            if hasattr(self, "project_id") and self.project_id
            else False,
            "default_mrp_production_id": self.id,
        }
        return action
