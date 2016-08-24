# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp import exceptions
from openerp.tools.translate import _

class hr_timesheet_invoice_factor(models.Model):
    _name = "hr_timesheet_invoice.factor"
    _description = "Invoice Rate"

    name = fields.Char(string='Internal Name', required=True, translate=True)
    customer_name = fields.Char(string='Name', help="Label for the customer")
    factor = fields.Float(string='Discount (%)', required=True, help="Discount in percentage")

class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    sale_subscription_id = fields.Many2one(comodel_name='sale.subscription',string="Subscription",related='account_id.first_subscription_id', store=False)

    invoice_id = fields.Many2one(comodel_name='account.invoice', string='Invoice')
    to_invoice = fields.Many2one(comodel_name='hr_timesheet_invoice.factor', string='Invoiceable', help="It allows to set the discount while making invoice, keep empty if the activities should not be invoiced.")

    """
    @api.v7
    def write(self, cr, uid, ids, vals, context=None):
        self._check_inv(cr, uid, ids, vals)
        return super(account_analytic_line,self).write(cr, uid, ids, vals,
                context=context)
    @api.v7
    def _check_inv(self, cr, uid, ids, vals):
        select = ids
        if isinstance(select, (int, long)):
            select = [ids]
        if ( not vals.has_key('invoice_id')) or vals['invoice_id' ] == False:
            for line in self.browse(cr, uid, select):
                if line.invoice_id:
                    raise exceptions.Warning(_('Error!'), _('You cannot modify an invoiced analytic line!'))
        return True
    """

class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.v7
    def _get_analytic_lines(self, cr, uid, ids, context=None):
        iml = super(account_invoice, self)._get_analytic_lines(cr, uid, ids, context=context)

        inv = self.browse(cr, uid, ids, context=context)[0]
        if inv.type == 'in_invoice':
            obj_analytic_account = self.pool.get('account.analytic.account')
            for il in iml:
                if il['account_analytic_id']:
		    # *-* browse (or refactor to avoid read inside the loop)
                    to_invoice = obj_analytic_account.read(cr, uid, [il['account_analytic_id']], ['to_invoice'], context=context)[0]['to_invoice']
                    if to_invoice:
                        il['analytic_lines'][0][2]['to_invoice'] = to_invoice[0]
        return iml

class account_move_line(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def create_analytic_lines(self):
        res = super(account_move_line, self).create_analytic_lines()
        for move_line in self:
            #For customer invoice, link analytic line to the invoice so it is not proposed for invoicing in Bill Tasks Work
            invoice_id = move_line.invoice_id and move_line.invoice_id.type in ('out_invoice', 'out_refund') and move_line.invoice_id or False
            # Only if 'invoice_id' exists because lines could be created outside an invoice system, for instance in expenses
            if invoice_id:
            	for line in move_line.analytic_line_ids:
	                line.invoice_id = invoice_id.id
                	line.to_invoice = line.to_invoice.id or False
        return res
