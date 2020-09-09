# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class MailActivity(models.Model):

    _inherit = 'mail.activity'

    # is_allow_document = fields.Boolean()
    def get_mail_activity(self):
        m = self.env[self.res_model].search([('id', '=', self.res_id)])
        return {
            'type': 'ir.actions.act_window',
            'name': self.res_model,
            'res_model': self.res_model,
            'res_id': m.id,
            'view_type': 'form',
            'view_mode': 'form',
        }