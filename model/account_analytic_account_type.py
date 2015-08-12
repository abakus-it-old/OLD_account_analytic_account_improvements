from openerp import models, fields, api

class account_analytic_account_type(models.Model):
    _name = 'account.analytic.account.type'

    name = fields.Char(string="Name", required=True)
    timesheet_product = fields.Many2one('product.product', string="Product", index=True)