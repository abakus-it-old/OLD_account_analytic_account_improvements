# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_analytic_account_team(models.Model):
    _name = 'account.analytic.account.team'
    
    name = fields.Char(string="Name", required=True)
    compagny = fields.Many2one('res.company', string="Compagny")
    active = fields.Boolean(string="Active", default=True)
    users = fields.Many2many('res.users', string="Users")