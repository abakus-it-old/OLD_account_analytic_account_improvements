from openerp import models, fields, api

class account_analytic_account_team(models.Model):
    _name = 'sale.subscription.team'
    
    name = fields.Char(string="Name", required=True)
    compagny = fields.Many2one('res.company', string="Compagny", index=True)
    active = fields.Boolean(string="Active", default=True)
    users = fields.Many2many('res.users',string="Users")