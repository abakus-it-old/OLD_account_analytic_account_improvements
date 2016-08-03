from openerp import models, fields

class account_analytic_account_improvements(models.Model):
    _inherit = ['account.analytic.account']

    def _default_first_subscription(self):
        cr = self.env.cr
        uid = self.env.user.id
        if self.subscription_ids and len(self.subscription_ids) > 0 :
            return self.subscription_ids[0]

    first_subscription_id = fields.Many2one(comodel_name='sale.subscription',string="Subscription", default=_default_first_subscription, store=False)
