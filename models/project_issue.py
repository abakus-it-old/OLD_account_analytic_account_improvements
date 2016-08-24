# -*- coding: utf-8 -*-

from openerp import models, api

class project_issue_add_partner_id_to_followers(models.Model):
    _inherit = 'project.issue'

    @api.model
    def create(self, vals):
        res = super(project_issue_add_partner_id_to_followers, self).create(vals)

        #add issue contact to the followers
        if vals and vals.get('partner_id'):
            self.env['mail.followers'].create({
                    'res_id' :  res.id,
                    'res_model' : 'project.issue',
                    'partner_id': vals.get('partner_id'),
                    })
        return res