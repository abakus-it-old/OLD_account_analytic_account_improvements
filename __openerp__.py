{
    'name': "AbAKUS contract improvements",
    'version': '1.0',
    'depends': ['account_analytic_analysis'],
    'author': "Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Contract',
    'description': """This modules adds some functionalities to the contracts for AbAKUS. 

It adds:
	- Team management for contracts, allows to create teams with users and link them to contracts
	- Type management for contracts, allows to create types with a product, a price and link them to contracts
	- BL invoicing: enable to invoice regarding the AbAKUS invoicing policy in BL Support contracts
	- New management of issues stages
		- Auto set assigned stage when issue assigned

This module has been developed by Bernard Delhez, intern @ AbAKUS it-solutions, under the control of Valentin Thirion.""",
    'data': ['account_analytic_account_view.xml','security/ir.model.access.csv',],
    'demo': [],
}
