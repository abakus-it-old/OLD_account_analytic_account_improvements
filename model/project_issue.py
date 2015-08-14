from openerp.osv import osv

class project_issue_add_partner_id_to_followers(osv.Model):
    _inherit = ['project.issue']
 
    def create(self, cr, uid, vals, context=None):
        res = super(project_issue_add_partner_id_to_followers, self).create(cr, uid, vals, context=context)
        
        #add issue contact to the followers
        if vals and vals.get('partner_id'):
            self.pool.get('mail.followers').create(cr,uid,{
                    'res_id' :  res,
                    'res_model' : 'project.issue',
                    'partner_id': vals.get('partner_id'),
                    })
                    
        return res