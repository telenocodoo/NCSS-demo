# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CrmProjectOwner(models.Model):
    _name = 'crm.project.owner'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    parent_id = fields.Many2one('crm.project.owner')


class CrmProjectPosition(models.Model):
    _name = 'crm.project.position'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char()


class CrmProjectStages(models.Model):
    _name = 'crm.project.stages'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char()


class CrmProjectBiddersRole(models.Model):
    _name = 'crm.project.bidders.role'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char()


class InvolvedContactRole(models.Model):
    _name = 'involved.contact.role'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char()


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_project_id = fields.Many2one('crm.project')
    involved_contact_ids = fields.One2many('involved.contact.lines', 'crm_id', copy=True)


class CrmProject(models.Model):
    _name = 'crm.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    description = fields.Text()
    crm_project_owner_id = fields.Many2one('crm.project.owner', 'Owner')
    stage_id = fields.Many2one('crm.project.stages', 'Stage')
    start_date = fields.Date(default=fields.Date.today())
    end_date = fields.Date()
    value = fields.Float()
    city_id = fields.Many2one('res.country.state')

    owner_contact_line_ids = fields.One2many('crm.project.line', 'crm_project_id', copy=True)
    bidder_line_ids = fields.One2many('bidder.lines', 'crm_project_id', copy=True)
    winner_line_ids = fields.One2many('winner.lines', 'crm_project_id', copy=True)


class CrmProjectLines(models.Model):
    _name = 'crm.project.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    crm_project_id = fields.Many2one('crm.project')

    crm_project_owner_id = fields.Many2one('crm.project.owner', 'Owner')
    crm_project_contact_id = fields.Many2one('crm.project.owner', 'Contact')
    job_position_id = fields.Many2one('crm.project.position')
    notes = fields.Char()


class BidderLines(models.Model):
    _name = 'bidder.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    crm_project_id = fields.Many2one('crm.project')

    bidder_id = fields.Many2one('res.partner', 'Bidder')
    bidder_role_id = fields.Many2one('crm.project.bidders.role', 'Bidder Role')


class WinnerLines(models.Model):
    _name = 'winner.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    crm_project_id = fields.Many2one('crm.project')
    crm_id = fields.Many2one('crm.lead')

    company_id = fields.Many2one('res.partner', 'Company')
    company_role = fields.Char('Company Role')
    company_role_id = fields.Many2one('crm.project.bidders.role', 'Company Role')
    involved_contact_id = fields.Many2one('res.partner', 'Involved Contact')
    involved_contact_role_id = fields.Many2one('involved.contact.role', 'Involved Contact Role')
    notes = fields.Char()
    is_crm = fields.Boolean()
    is_bidder = fields.Boolean()
    project_number = fields.Integer()

    def create_opportunity(self):
        for record in self:
            crm_id = self.env['crm.lead'].search([('crm_project_id', '=', record.crm_project_id.id),
                                                  ('partner_id', '=', record.company_id.id),
                                                  ], limit=1)
            if crm_id:
                self.env['involved.contact.lines'].create({
                    'crm_id': crm_id.id,
                    'involved_contact_id': record.involved_contact_id.id,
                    'involved_contact_role_id': record.involved_contact_role_id.id
                })
                record.crm_id = crm_id.id
            else:
                crm_obj = self.env['crm.lead'].create({
                    'name': record.crm_project_id.name + "/" + record.company_id.name,
                    'partner_id': record.company_id.id,
                    'crm_project_id': record.crm_project_id.id
                })
                self.env['involved.contact.lines'].create({
                    'crm_id': crm_obj.id,
                    'involved_contact_id': record.involved_contact_id.id,
                    'involved_contact_role_id': record.involved_contact_role_id.id
                })
                record.crm_id = crm_obj.id
            record.is_crm = True

    # @api.onchange('is_bidder')
    # def onchange_is_bidder(self):
    #     bidders = []
    #     for record in self:
    #         bidder_id = self.env['bidder.lines'].search([('crm_project_id.id', '=', record.project_number)])
    #                                                      # ('bidder_id', '=', self.company_id.id)
    #         print(bidder_id)
    #         for bidder in bidder_id:
    #             bidders.append(bidder.bidder_id.id)
    #     domain = {'company_id': [('id', 'in', bidders)]}
    #     return {'domain': domain}

    @api.onchange('company_id')
    def onchange_company_id(self):
        for record in self:
            bidders = self.env['bidder.lines'].search([('crm_project_id.id', '=', record.project_number),
                                                       ('bidder_id', '=', self.company_id.id)], limit=1)
            # print(bidders)
            record.company_role_id = bidders.bidder_role_id.id


class InvolvedContactLines(models.Model):
    _name = 'involved.contact.lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    crm_id = fields.Many2one('crm.lead')

    involved_contact_id = fields.Many2one('res.partner', 'Involved Contact')
    involved_contact_role_id = fields.Many2one('involved.contact.role', 'Involved Contact Role')


