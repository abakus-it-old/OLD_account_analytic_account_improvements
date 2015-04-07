from openerp import models, fields, api
import datetime
from datetime import date

class account_analytic_account_team(models.Model):
    _name = 'account.analytic.account.team'
    
    name = fields.Char(string="Name", required=True)
    compagny = fields.Many2one('res.company', string="Compagny", index=True)
    active = fields.Boolean(string="Active", default=True)
    users = fields.Many2many('res.users',string="Users")

class account_analytic_account_type(models.Model):
    _name = 'account.analytic.account.type'

    name = fields.Char(string="Name", required=True)
    timesheet_product = fields.Many2one('product.product', string="Product", index=True)
    
class account_analytic_account_improvements(models.Model):
    _inherit = ['account.analytic.account']
    timesheet_product_price = fields.Float("Hourly Rate")
    contract_type = fields.Many2one('account.analytic.account.type', string="Type", index=True, required=True)
    contract_team = fields.Many2one('account.analytic.account.team', string="Team", index=True)
    contract_type_product_name = fields.Char(compute='_get_product_name',string="Product name", store=False)
    number_of_timesheets = fields.Integer(compute='_compute_number_of_timesheets',string="Number of timesheets", store=False)
    total_invoice_amount = fields.Float(compute='_compute_total_invoice_amount',string="Total invoice amount", store=False)
    computed_units_consumed = fields.Float(compute='_compute_units_consumed',string="Units Consumed", store=False)
    computed_units_remaining = fields.Float(compute='_compute_units_remaining',string="Units Remaining", store=False)
    total_invoice_amount_info = fields.Char(compute='_compute_total_invoice_amount_info',string="Total invoice amount", store=False)


    @api.one
    def _compute_units_consumed(self):
        cr = self.env.cr
        uid = self.env.user.id
        account_analytic_line_obj = self.pool.get('account.analytic.line')
        account_analytic_lines = account_analytic_line_obj.search(cr, uid, [('invoice_id', '=', False),('account_id','=',self.id)])
        total=0
        if account_analytic_lines:
            for val in account_analytic_line_obj.browse(cr, uid, account_analytic_lines):
                total += val.unit_amount
        self.computed_units_consumed = total
    
    @api.one
    def _compute_units_remaining(self):
        self.computed_units_remaining = self.quantity_max - self.computed_units_consumed
    
    @api.one
    @api.onchange('contract_type')
    def _get_price(self):
        self.timesheet_product_price = self.contract_type.timesheet_product.lst_price
    
    @api.one
    @api.onchange('contract_type')
    def _get_product_name(self):
        self.contract_type_product_name = self.contract_type.timesheet_product.name
    
    @api.one
    def _compute_number_of_timesheets(self):
        cr = self.env.cr
        uid = self.env.user.id
        account_analytic_line_obj = self.pool.get('account.analytic.line')
        account_analytic_lines = account_analytic_line_obj.search(cr, uid, [('invoice_id', '=', False),('account_id','=',self.id)])
        self.number_of_timesheets = len(account_analytic_lines)
    
    @api.one
    @api.onchange('contract_type')  
    def _compute_total_invoice_amount(self):
        service_delivery_total = 0
        working_hours_total = 0
        prepaid_instalment_total = 0
        on_site_total=0							
        price = self.timesheet_product_price
        for line in self.line_ids:
            if line.ref:
                prepaid_instalment_total += line.amount
            if not line.ref:
                if line.on_site:
                    computed_amount = self.on_site_product.lst_price
                    on_site_total += 1
                else:
                    computed_amount=0
                computed_amount=computed_amount + ((price * line.unit_amount)*((100-line.to_invoice.factor)/100))
                service_delivery_total += computed_amount
                working_hours_total += line.unit_amount
        self.total_invoice_amount = prepaid_instalment_total - service_delivery_total
    
    @api.one
    @api.onchange('contract_type')  
    def _compute_total_invoice_amount_info(self):
        balance = self.total_invoice_amount
        if balance >= 0:
            info = 'In favour of the customer'
        if balance < 0:
            info = 'In our favour'
        self.total_invoice_amount_info = str(balance)+" euros ("+info+")"

    @api.multi
    def create_invoice(self):
        cr = self.env.cr
        uid = self.env.user.id
        account_analytic_line_obj = self.pool.get('account.analytic.line')
        account_analytic_lines = account_analytic_line_obj.search(cr, uid, [('invoice_id', '=', False),('account_id','=',self.id)])

        total = self.total_invoice_amount
        if total>0:
            today = datetime.datetime.now()
            
            #search the right sale journal         
            account_journal_obj = self.pool.get('account.journal')
            account_journal = account_journal_obj.search(cr, uid, [('company_id', '=', self.company_id.id),('type','=','sale')]) #('analytic_journal_id', '=', account_analytic_journal[0])

            invoice_id = self.pool.get('account.invoice').create(cr,uid,{
                'account_id' :  self.partner_id.property_account_receivable.id,
                'company_id' : self.company_id.id,
                'currency_id' : self.currency_id.id,
                'journal_id' : account_journal_obj.browse(cr, uid, account_journal[0]).id,
                'partner_id' : self.partner_id.id,
                'date_invoice' : today.strftime('%Y-%m-%d'),
                'state' : 'draft',
                'reference_type' : 'none', 
                })

                
            if self.contract_type.timesheet_product.property_account_income.id:
                invoice_line_account_id = self.contract_type.timesheet_product.property_account_income.id
            else:
                invoice_line_account_id = self.contract_type.timesheet_product.categ_id.property_account_income_categ.id
                
            invoice_line_id = self.pool.get('account.invoice.line').create(cr,uid,{
                'invoice_id' : invoice_id,
                'product_id' : self.contract_type.timesheet_product.id,
                'name' : self.contract_type.timesheet_product.description_sale,
                'quantity' : total/self.timesheet_product_price,
                'price_unit' : self.timesheet_product_price,
                'account_id' : invoice_line_account_id,
                })
            
            #what is the return of self.contract_type.timesheet_product.taxes_id (many2many)
            for tax in self.contract_type.timesheet_product.taxes_id:
                if tax.company_id.id == self.company_id.id:
                    cr.execute('insert into  account_invoice_line_tax (invoice_line_id, tax_id) values(%s,%s)',(invoice_line_id,tax.id))

            for val in account_analytic_line_obj.browse(cr, uid, account_analytic_lines):
                account_analytic_line_obj.write(cr, uid, val.id, {'invoice_id': invoice_id})   
            
            #reinitialize the Units Consumed/Units Remaining counters
            self.hours_quantity = 0
            self.remaining_hours = self.quantity_max
            self.last_invoice_date = today.strftime('%Y-%m-%d')
            self.invoice_on_timesheets = False
            
            #redirect to Customer Invoices menu
            ir_ui_menu_obj = self.pool.get('ir.ui.menu')
            ir_ui_menus = ir_ui_menu_obj.search(cr, uid, [('name', '=', 'Customer Invoices')])
            if ir_ui_menus:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                    'params': {'menu_id': ir_ui_menu_obj.browse(cr, uid, ir_ui_menus[0]).id }
                }
