# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'
    transfer_to_ids = fields.Many2many('administrative.communication.management')
    # a_contact_id = fields.Many2one('administrative.communication.contact')
