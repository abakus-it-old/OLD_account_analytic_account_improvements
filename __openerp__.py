{
    'name': "AbAKUS contract improvements",
    'version': '9.0.1.0',
    'depends': ['sale_contract', 'contract_timesheet_activities_on_site_management'],
    'author': "Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Contract',
    'description': """This modules adds some functionalities to the contracts for AbAKUS. 

It adds:
    - Team management for contracts, allows to create teams with users and link them to contracts
    - Type management for contracts (mandatory), allows to create types with a product, a price and link them to contracts
    - Minimum contractual amount in contract types, that is added to contracts also
    - BL invoicing: enable to invoice regarding the AbAKUS invoicing policy in BL Support contracts
    - New stages in contracts: negociation,open,pending,close,cancelled,refused
    - on_change_template refresh the new attributes: type, team, hourly rate
    - "project auto create": 
        - if you create a new contract then the default values come from the project of the contract template.
        - default values: 
            - Project: team, stages, color, privacy_visibility, date_start, date and project_escalation_id.
        - followers:
            - project: none
            - task: Assigned to, Reviewer and task creator
            - issue: Assigned to, Contact and issue creator

TODO:
    - Create Project Template

odoo 9 Updates:
    - Invoiceable field (model + view integration) (not exists in odooV9)
    - issue/task stage managment in project view
    - project color managment in projet view
    - first_subscription_id for account.analytic.account
    - sale_subscription_id for account.analytic.line

This module has been developed by Bernard Delhez, intern @ AbAKUS it-solutions, under the control of Valentin Thirion.""",
    'data': ['view/sale_subscription_view.xml',
             'view/account_analytic_account_view.xml',
             'view/account_analytic_account_type_view.xml',
             'view/account_analytic_account_team_view.xml',
             'view/project_project_view.xml',
             'view/account_analytic_line_view.xml',
             'view/project_issue_view.xml',
             'security/ir.model.access.csv',],
}
