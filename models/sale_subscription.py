# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

class sale_subscription_improvements(models.Model):
    _inherit = 'sale.subscription'
    
    timesheet_product_price = fields.Float("Hourly Rate")
    contract_type = fields.Many2one('account.analytic.account.type', string="Type")
    contract_team = fields.Many2one('account.analytic.account.team', string="Team")
    contract_type_product_name = fields.Char(compute='_get_product_name', string="Product name", store=False)
    number_of_timesheets = fields.Integer(compute='_compute_number_of_timesheets', string="Number of timesheets", store=False)
    total_invoice_amount = fields.Float(compute='_compute_total_invoice_amount', string="Total invoice amount", store=False)
    computed_units_consumed = fields.Float(compute='_compute_units_consumed', string="Units Consumed", store=False)
    computed_units_remaining = fields.Float(compute='_compute_units_remaining', string="Units Remaining", store=False)
    total_invoice_amount_info = fields.Char(compute='_compute_total_invoice_amount_info', string="Total invoice amount", store=False)
    contractual_minimum_amount = fields.Float(string="Contractual minimum amount", store=True)
    quantity_max = fields.Float(string="Prepaid Service Unit")
    use_project = fields.Boolean(compute='_get_use_project', string="Use Project", store=False)
    project_id = fields.Many2one('project.project', compute="_compute_project", string="Project")

    state = fields.Selection([('template', 'Template'),
                              ('negociation','Negociation'),
                              ('draft','New'),
                              ('open','In Progress'),
                              ('pending','To Renew'),
                              ('close','Closed'),
                              ('cancelled', 'Cancelled'),
                              ('refused','Refused')], default='negociation')
    
    baseline = fields.Boolean(compute='_compute_is_baseline', string="Baseline contract", store=False)

    @api.one
    @api.depends('contract_type')
    def _compute_is_baseline(self):
        if self.contract_type:
            self.is_baseline = self.contract_type.is_baseline
        self.is_baseline = False
                              
    @api.one
    def _compute_units_consumed(self):
        total = 0
        for line in self.line_ids:
            total += line.unit_amount
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
    def _get_use_project(self):
        self.use_project = self.contract_type.use_project
        self.analytic_account_id.write({'use_tasks': self.use_project})
        self.analytic_account_id.write({'use_issues': self.use_project})

    @api.one
    @api.onchange('contract_type')
    def _compute_project(self):
        if self.use_project:
            if self.analytic_account_id:
                if len(self.analytic_account_id.project_ids) > 0:
                    self.project_id = self.analytic_account_id.project_ids[0]
                    self.project_id.write({'sale_subscription_id': self.id})

    @api.one
    @api.onchange('contract_type')
    def _get_product_name(self):
        self.contract_type_product_name = self.contract_type.timesheet_product.name
        self.contractual_minimum_amount = self.contract_type.contractual_minimum_amount
        self.quantity_max = self.contract_type.contractual_minimum_amount * 2

    @api.one
    def _compute_number_of_timesheets(self):
        num = 0
        for line in self.line_ids:
            if line.is_timesheet:
                num += 1
        self.number_of_timesheets = num

    @api.one
    @api.onchange('contract_type')
    def _compute_total_invoice_amount(self):

        service_delivery_total = 0
        working_hours_total = 0
        prepaid_instalment_total = 0
        on_site_total=0
        price = self.timesheet_product_price
        travel_cost = 0
        cr = self.env.cr

        if self.on_site_invoice_by_km:
            travel_cost = self.on_site_product.lst_price * self.on_site_distance_in_km
        else:
            travel_cost = self.on_site_product.lst_price

        for line in self.line_ids:
            #check if invoice exists for the current line
            if line.move_id and not line.is_timesheet:
                computed_amount = line.amount
                prepaid_instalment_total += computed_amount
            else:
                if line.on_site:
                    computed_amount = travel_cost
                    on_site_total += 1
                else:
                    computed_amount = 0
                computed_amount = computed_amount + ((price * line.unit_amount) * ((100 - line.to_invoice.factor) / 100) )

                service_delivery_total += computed_amount
                working_hours_total += line.unit_amount

            #check if line amount is ok, else set the computed amount
            if line.amount == 0:
                cr.execute("update account_analytic_line set amount=%s where id=%s" % (str(computed_amount), str(line.id)))
                cr.commit()

        self.total_invoice_amount = round(prepaid_instalment_total - service_delivery_total,2)

    @api.one
    @api.onchange('contract_type')
    def _compute_total_invoice_amount_info(self):
        balance = self.total_invoice_amount
        if balance >= 0:
            info = 'In favour of the customer'
        if balance < 0:
            info = 'In favour of ' + self.company_id.name
        self.total_invoice_amount_info = str(abs(balance))+' '+u"\u20AC"+" ("+info+")" # u20AC == euro sign

    @api.multi
    def create_invoice(self):
        cr = self.env.cr
        uid = self.env.user.id
        account_analytic_line_obj = self.pool.get('account.analytic.line')

        account_analytic_lines = account_analytic_line_obj.search(cr, uid, [('invoice_id', '=', False),('account_id','=',self.analytic_account_id.id)])

        total = self.total_invoice_amount
        if total < 0:
            today = datetime.datetime.now()
            total_to_invoice = total * (-1)

            #search the right sale journal
            account_journal_obj = self.pool.get('account.journal')
            account_journal = account_journal_obj.search(cr, uid, [('company_id', '=', self.company_id.id),('type','=','sale')]) #('analytic_journal_id', '=', account_analytic_journal[0])

            invoice_id = self.pool.get('account.invoice').create(cr,uid,{
                'account_id' :  self.partner_id.property_account_receivable_id.id,
                'company_id' : self.company_id.id,
                'currency_id' : self.currency_id.id,
                'journal_id' : account_journal_obj.browse(cr, uid, account_journal[0]).id,
                'partner_id' : self.partner_id.id,
                'date_invoice' : today.strftime('%Y-%m-%d'),
                'state' : 'draft',
                'reference_type' : 'none',
		        'fiscal_position' : self.partner_id.property_account_position_id.id,
		        'payment_term' : self.partner_id.property_payment_term_id.id,
                })

            if self.contract_type.timesheet_product.property_account_income_id.id:
                invoice_line_account_id = self.contract_type.timesheet_product.property_account_income_id.id
            else:
                invoice_line_account_id = self.contract_type.timesheet_product.categ_id.property_account_income_categ_id.id

            invoice_line_id = self.pool.get('account.invoice.line').create(cr, uid, {
                'invoice_id' : invoice_id,
                'product_id' : self.contract_type.timesheet_product.id,
                'name' : self.contract_type.name,
                'quantity' : total_to_invoice/self.timesheet_product_price,
                'price_unit' : self.timesheet_product_price,
                'account_id' : invoice_line_account_id,
                'account_analytic_id' : self.analytic_account_id.id,
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

    def project_create(self, cr, uid, analytic_account_id, vals, context=None):
        '''
        This function is called at the time of analytic account creation and is used to create a project automatically linked to it if the conditions are meet.
        '''
        #code from the project_create method from the project module odooV8
        """
        project_pool = self.pool.get('project.project')
        project_id = project_pool.search(cr, uid, [('analytic_account_id','=', analytic_account_id)])
        if not project_id and self._trigger_project_creation(cr, uid, vals, context=context):
            project_values = {
                'name': vals.get('name'),
                'analytic_account_id': analytic_account_id,
                'type': vals.get('type','contract'),
            }
            return project_pool.create(cr, uid, project_values, context=context)
        return False
        """

        project_id = super(sale_subscription_improvements, self).project_create(cr, uid, analytic_account_id, vals, context=context)
        if project_id:
            project_project_obj = self.pool.get('project.project')
            project_project = project_project_obj.browse(cr, uid, project_id)

            if project_project.sale_subscription_id:
                project_project_template_ids = project_project_obj.search(cr, uid, [('analytic_account_id', '=', project_project.sale_subscription_id.contract_type.project_template_id.id)])

                if project_project_template_ids:
                    project_project_template = project_project_obj.browse(cr, uid, project_project_template_ids[0])

                    #Sets the project attributes
                    #'''''''''''''''''''''''''''

                    #Adds the team users from the analytic account in the project team
                    #-----------------------------------------------------------------

                    #if project_project.analytic_account_id.contract_team:
                    #    for user in project_project.analytic_account_id.contract_team.users:
                    #        query = """
                    #                INSERT INTO project_user_rel (uid, project_id)
                    #                VALUES (%s,%s)
                    #                """
                    #        cr.execute(query, (str(user.id),str(project_id)))


                    #Attributes in page "Other Info"
                    #-------------------------------
                    project_project.color = project_project_template.color
                    project_project.privacy_visibility = project_project_template.privacy_visibility
                    #project_project.date_start = project_project.analytic_account_id.date_start
                    #project_project.date = project_project.analytic_account_id.date
                    #project_project.project_escalation_id = project_project_template.project_escalation_id.id

                    #Sets the project stages
                    #-----------------------
                    #Removes the old project stages
                    query = """
                            DELETE FROM project_task_type_rel
                            WHERE project_id=%s
                            """
                    cr.execute(query, [str(project_id)])

                    #Adds the new project stages from the project template
                    for stage in project_project_template.type_ids:
                        query = """
                                INSERT INTO project_task_type_rel (type_id, project_id)
                                VALUES (%s,%s)
                                """
                        cr.execute(query, (str(stage.id),str(project_id)))


                    #removes the project followers
                    #query = """
                    #        DELETE FROM mail_followers
                    #        WHERE res_id=%s and res_model=%s
                    #        """
                    #cr.execute(query, (str(project_id), 'project.issue'))


        return project_id

    def on_change_template(self, cr, uid, ids, template_id, date_start=False, context=None):
        #code from the on_change_template method from the analytic module
        """
        if not template_id:
            return {}
        res = {'value':{}}
        template = self.browse(cr, uid, template_id, context=context)
        if template.date_start and template.date:
            from_dt = datetime.strptime(template.date_start, tools.DEFAULT_SERVER_DATE_FORMAT)
            to_dt = datetime.strptime(template.date, tools.DEFAULT_SERVER_DATE_FORMAT)
            timedelta = to_dt - from_dt
            res['value']['date'] = datetime.strftime(datetime.now() + timedelta, tools.DEFAULT_SERVER_DATE_FORMAT)
        if not date_start:
            res['value']['date_start'] = fields.date.today()
        res['value']['quantity_max'] = template.quantity_max
        res['value']['parent_id'] = template.parent_id and template.parent_id.id or False
        res['value']['description'] = template.description
        return res
        """

        dict = super(sale_subscription_improvements, self).on_change_template(cr, uid, ids, template_id, date_start)
        if 'value' in dict:
            template = self.browse(cr, uid, template_id, context=context)
            dict['value']['contract_type'] = template.contract_type.id
            dict['value']['timesheet_product_price'] = template.timesheet_product_price
            dict['value']['contract_team'] = template.contract_team.id
            dict['value']['contractual_minimum_amount'] = template.contractual_minimum_amount
            dict['value']['quantity_max'] = template.contractual_minimum_amount * 2
        return dict
