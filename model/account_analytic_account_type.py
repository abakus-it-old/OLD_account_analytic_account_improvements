from openerp import models, fields, api

class account_analytic_account_type(models.Model):
    _name = 'sale.subscription.type'

    name = fields.Char(string="Name", required=True)
    timesheet_product = fields.Many2one('product.product', string="Product", index=True)
    contractual_minimum_amount = fields.Float(string="Contractual minimum amount", store=True, index=True)
