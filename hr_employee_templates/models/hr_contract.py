from odoo import api, fields, models, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    contract_type = fields.Selection([('saudi_contract', 'Saudi Contract'),
                                        ('foreign_saudi_contract', 'Foreign Saudi Contract'),
                                        ('advisor_contract', 'Advisor Contract'),
                                        ('cooperation_contract', 'Cooperation Contract'),
                                        ], string='Contract Type', default='saudi_contract')
