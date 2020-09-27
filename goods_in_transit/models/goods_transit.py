# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class GoodsContainer(models.Model):
    _name = 'goods.container'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()


class GoodsTransit(models.Model):
    _name = 'goods.transit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Vendor')
    location_id = fields.Many2one('stock.location', 'Location')
    po_line_ids = fields.One2many('goods.transit.line', 'goods_transit_id')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        domain = [('id', 'in', self.partner_id.location_ids.ids)]
        return {'domain': {'location_id': domain}}

    def action_stock_move(self):
        purchase_order_obj = self.po_line_ids.mapped('po_line_id.order_id')
        destination_location_obj = self.po_line_ids.mapped('destination_location_id')
        move_lst = []
        res = []
        for purchase in purchase_order_obj:
            print("purchase", purchase)
            for destination in destination_location_obj:
                print("destination", destination)
                for gnt in self.po_line_ids:
                    if gnt.po_line_id.order_id.id == purchase.id \
                       and gnt.destination_location_id.id == destination.id:
                        print("GNT:::::::::::", gnt)
                        values = {
                            'partner_id': gnt.partner_id.id,
                            'product_id': gnt.po_line_id.product_id.id,
                            'purchase_line_id': gnt.po_line_id.id,
                            'product_uom': gnt.po_line_id.product_uom.id,
                            'product_uom_qty': gnt.po_line_id.product_qty,
                            'name': gnt.po_line_id.name,
                            'location_id': gnt.location_id.id,
                            'location_dest_id': gnt.destination_location_id.id,
                            'origin': gnt.po_line_id.order_id.name,
                            'picking_type_id': gnt.po_line_id.order_id.picking_type_id.id,
                        }


                        if gnt.po_line_id.product_id.type not in ['product', 'consu']:
                            print("nooooooooooooooooooooooooooooooooo")
                            return res
                        qty = 0.0
                        price_unit = gnt.po_line_id._get_stock_move_price_unit()
                        for move in gnt.po_line_id.move_ids.filtered(
                                lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
                            qty += move.product_uom._compute_quantity(gnt.received_qty, gnt.po_line_id.product_uom,
                                                                      rounding_method='HALF-UP')

                        values = {
                            # truncate to 2000 to avoid triggering index limit error
                            # TODO: remove index in master?
                            'name': (gnt.po_line_id.name or '')[:2000],
                            'product_id': gnt.po_line_id.product_id.id,
                            'product_uom': gnt.po_line_id.product_uom.id,
                            'date': gnt.po_line_id.order_id.date_order,
                            'date_expected': gnt.po_line_id.date_planned,
                            'location_id': gnt.location_id.id,
                            'location_dest_id': gnt.destination_location_id.id,
                            'product_uom_qty': gnt.received_qty,
                            'picking_id': False,
                            'partner_id': gnt.partner_id.id,
                            'move_dest_ids': [(4, x) for x in gnt.po_line_id.move_dest_ids.ids],
                            'state': 'draft',
                            'purchase_line_id': gnt.po_line_id.id,
                            'company_id': gnt.po_line_id.order_id.company_id.id,
                            'price_unit': price_unit,
                            'picking_type_id': gnt.po_line_id.order_id.picking_type_id.id,
                            'group_id': gnt.po_line_id.order_id.group_id.id,
                            'origin': gnt.po_line_id.order_id.name,
                            'propagate_date': gnt.po_line_id.propagate_date,
                            'propagate_date_minimum_delta': gnt.po_line_id.propagate_date_minimum_delta,
                            'description_picking': gnt.po_line_id.product_id._get_description(gnt.po_line_id.order_id.picking_type_id),
                            'propagate_cancel': gnt.po_line_id.propagate_cancel,
                            'route_ids': gnt.po_line_id.order_id.picking_type_id.warehouse_id and [
                                (6, 0, [x.id for x in gnt.po_line_id.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                            'warehouse_id': gnt.po_line_id.order_id.picking_type_id.warehouse_id.id,
                        }
                        diff_quantity = gnt.po_line_id.product_qty - qty
                        if float_compare(diff_quantity, 0.0, precision_rounding=gnt.po_line_id.product_uom.rounding) > 0:
                            po_line_uom = gnt.po_line_id.product_uom
                            quant_uom = gnt.po_line_id.product_id.uom_id
                            product_uom_qty, product_uom = po_line_uom._adjust_uom_quantities(diff_quantity, quant_uom)
                            values['product_uom_qty'] = gnt.received_qty
                            values['product_uom'] = product_uom.id
                        res.append(values)
                        move_lst.append(values)
                print(">>>>>>>>>>>>>>>>>>>>", res)
                print(move_lst)
                if move_lst:
                    stock = self.env['stock.picking']
                    stock_move_obj = self.env['stock.move']
                    stock_obj = stock.create({
                        'partner_id': move_lst[0]['partner_id'],
                        'picking_type_id': move_lst[0]['picking_type_id'],
                        'goods_in_transit_id': self.id,
                        'location_id': move_lst[0]['location_id'],
                        'location_dest_id': move_lst[0]['location_dest_id'],
                        'origin': move_lst[0]['origin'],
                    })
                    print("SSSSSSSSSSSSS", stock_obj)
                    for move in move_lst:
                        print("moveeeeeeeeeeeeeeeeeeeeeee", move)
                        move['picking_id'] = stock_obj.id
                        print("move edit", move)
                        stock_move_obj.create(move)._action_confirm()._action_assign()
                        #     {
                        #     'picking_id': stock_obj.id,
                        #     'product_id': move['product_id'],
                        #     'purchase_line_id': move['purchase_line_id'],
                        #     'product_uom': move['product_uom'],
                        #     'location_id': move['location_id'],
                        #     'location_dest_id': move['location_dest_id'],
                        #     'product_uom_qty': move['product_uom_qty'],
                        #     'name': move['name'],
                        # })
                    move_lst.clear()

    def get_stock_moves_related_to_gnt(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'All Transfers',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('goods_in_transit_id', '=', self.id)],
            'target': 'current',
        }


class CustodyRequestLine(models.Model):
    _name = 'goods.transit.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_partner_related_locations(self):
        for record in self:
            if record.partner_id and record.location_id:
                domain = [('partner_id.id', '=', record.partner_id.id),
                          ('location_id.id', '=', record.location_id.id),
                          ('qty_remaining', '>', 0.0),
                          ('id', 'not in', self.goods_transit_id.po_line_ids.mapped('po_line_id').ids)
                          ]
                return domain

    goods_transit_id = fields.Many2one('goods.transit')
    po_line_id = fields.Many2one('purchase.order.line',
                                 domain=get_partner_related_locations,
                                 string='purchase order line')
    purchase_order_id = fields.Many2one('purchase.order',
                                        related='po_line_id.order_id',
                                        string='purchase order')
    partner_id = fields.Many2one('res.partner', 'Vendor',)
    location_id = fields.Many2one('stock.location', 'source Location')
    destination_location_id = fields.Many2one('stock.location', 'Destination Location')
    remaining_qty = fields.Float(related='po_line_id.qty_remaining')
    received_qty = fields.Float()
    container_id = fields.Many2one('goods.container')

    @api.onchange('partner_id', 'location_id')
    def onchange_partner_id(self):
        domain = [('partner_id.id', '=', self.partner_id.id),
                  ('location_id.id', '=', self.location_id.id),
                  ('qty_remaining', '>', 0.0),
                  ('id', 'not in', self.goods_transit_id.po_line_ids.mapped('po_line_id').ids),
                  ]
        return {'domain': {'po_line_id': domain}}


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def get_partner_related_locations(self):
        domain = [('id', 'in', self.partner_id.location_ids.ids if self.partner_id else self.order_id.partner_id.location_ids.ids)]
        return domain

    qty_remaining = fields.Float(compute="compute_qty_remaining", store=True)
    goods_transit_id = fields.Many2one('goods.transit')
    location_id = fields.Many2one('stock.location', 'Location', domain=get_partner_related_locations)

    @api.onchange('partner_id', 'location_id')
    def onchange_partner_id(self):
        domain = [('id', 'in', self.partner_id.location_ids.ids)]
        return {'domain': {'location_id': domain}}

    @api.depends('product_qty', 'qty_received')
    def compute_qty_remaining(self):
        for record in self:
            record.qty_remaining = record.product_qty - record.qty_received

    # def _prepare_stock_moves(self, picking):
    #     """ Prepare the stock moves data for one order line. This function returns a list of
    #     dictionary ready to be used in stock.move's create()
    #     """
    #     print("moveeeeeeeeeeeeeeeeeeee")
    #     self.ensure_one()
    #     res = []
    #     if self.product_id.type not in ['product', 'consu']:
    #         return res
    #     qty = 0.0
    #     price_unit = self._get_stock_move_price_unit()
    #     for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
    #         qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
    #     template = {
    #         # truncate to 2000 to avoid triggering index limit error
    #         # TODO: remove index in master?
    #         'name': (self.name or '')[:2000],
    #         'product_id': self.product_id.id,
    #         'product_uom': self.product_uom.id,
    #         'date': self.order_id.date_order,
    #         'date_expected': self.date_planned,
    #         'location_id': self.order_id.partner_id.property_stock_supplier.id,
    #         'location_dest_id': self.order_id._get_destination_location(),
    #         'picking_id': picking.id,
    #         'partner_id': self.order_id.dest_address_id.id,
    #         'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
    #         'state': 'draft',
    #         'purchase_line_id': self.id,
    #         'company_id': self.order_id.company_id.id,
    #         'price_unit': price_unit,
    #         'picking_type_id': self.order_id.picking_type_id.id,
    #         'group_id': self.order_id.group_id.id,
    #         'origin': self.order_id.name,
    #         'propagate_date': self.propagate_date,
    #         'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
    #         'description_picking': self.product_id._get_description(self.order_id.picking_type_id),
    #         'propagate_cancel': self.propagate_cancel,
    #         'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
    #         'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
    #     }
    #     diff_quantity = self.product_qty - qty
    #     if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
    #         po_line_uom = self.product_uom
    #         quant_uom = self.product_id.uom_id
    #         product_uom_qty, product_uom = po_line_uom._adjust_uom_quantities(diff_quantity, quant_uom)
    #         template['product_uom_qty'] = product_uom_qty
    #         template['product_uom'] = product_uom.id
    #         res.append(template)
    #     return res
    #
    # def _create_or_update_picking(self):
    #     print("OOOOOOOOOOOOOOOOOOOOOOOOOOO")
    #     for line in self:
    #         if line.product_id and line.product_id.type in ('product', 'consu'):
    #             # Prevent decreasing below received quantity
    #             if float_compare(line.product_qty, line.qty_received, line.product_uom.rounding) < 0:
    #                 raise UserError(_('You cannot decrease the ordered quantity below the received quantity.\n'
    #                                   'Create a return first.'))
    #
    #             if float_compare(line.product_qty, line.qty_invoiced, line.product_uom.rounding) == -1:
    #                 # If the quantity is now below the invoiced quantity, create an activity on the vendor bill
    #                 # inviting the user to create a refund.
    #                 activity = self.env['mail.activity'].sudo().create({
    #                     'activity_type_id': self.env.ref('mail.mail_activity_data_warning').id,
    #                     'note': _('The quantities on your purchase order indicate less than billed. You should ask for a refund. '),
    #                     'res_id': line.invoice_lines[0].invoice_id.id,
    #                     'res_model_id': self.env.ref('account.model_account_move').id,
    #                 })
    #                 activity._onchange_activity_type_id()
    #
    #             # If the user increased quantity of existing line or created a new line
    #             pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit'))
    #             picking = pickings and pickings[0] or False
    #             if not picking:
    #                 res = line.order_id._prepare_picking()
    #                 picking = self.env['stock.picking'].create(res)
    #             move_vals = line._prepare_stock_moves(picking)
    #             for move_val in move_vals:
    #                 self.env['stock.move']\
    #                     .create(move_val)\
    #                     ._action_confirm()\
    #                     ._action_assign()


class ResPartner(models.Model):
    _inherit = 'res.partner'
    location_id = fields.Many2one('stock.location', 'Location')
    location_ids = fields.Many2many('stock.location', store=True)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    goods_in_transit_id = fields.Many2one('goods.transit')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_approve(self, force=False):
        print("approve")
        self.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
        self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            print(order)
            print(order._add_supplier_to_product)
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
                print(order.button_approve())
            else:
                order.write({'state': 'to approve'})
        return True
