# -*- coding: utf-8 -*-

from openerp.osv import osv

class mail_followers_remove_project_followers(osv.Model):
    _inherit = ['mail.followers']
 
    def create(self, cr, uid, vals, context=None):
        if context and context.get('alias_parent_model_name') == 'project.project':
            return False
        res = super(mail_followers_remove_project_followers, self).create(cr, uid, vals, context=context)
        return res