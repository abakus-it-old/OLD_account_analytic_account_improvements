# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sale_subscription_shared(models.Model):
    _name = 'sale.subscription.shared'

    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    
    @api.model
    def get_instance(self):
        return self.search([('id','=',1)], limit=1)
    
    @api.model
    def get_start_date(self):
        sale_subscription_shared = self.search([('id','=',1)], limit=1)
        if sale_subscription_shared:
            return sale_subscription_shared.start_date
        return None
        
    @api.model
    def get_end_date(self):
        sale_subscription_shared = self.search([('id','=',1)], limit=1)
        if sale_subscription_shared:
            return sale_subscription_shared.end_date
        return None