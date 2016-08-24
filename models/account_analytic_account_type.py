# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_analytic_account_type(models.Model):
    _name = 'account.analytic.account.type'

    name = fields.Char(string="Name", required=True)
    timesheet_product = fields.Many2one('product.product', string="Product")
    contractual_minimum_amount = fields.Float(string="Contractual minimum amount")
    use_project = fields.Boolean(string="Use Project")
    project_template_id = fields.Many2one('project.project', string="Project Template")
    is_baseline = fields.Boolean(string="Baseline contract")
