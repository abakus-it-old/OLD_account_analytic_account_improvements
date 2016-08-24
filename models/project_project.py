# -*- coding: utf-8 -*-

from openerp import models, fields

class projects_project_improvements(models.Model):
    _inherit = ['project.project']

    sale_subscription_id = fields.Many2one('sale.subscription', string="Subscription / Contract")
