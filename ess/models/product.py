from odoo.http import request
from odoo import models, api, fields,_


class Products(models.AbstractModel):
    _inherit = 'product.product'

    @api.model
    def get_product_obj(self, data):
        return self.env['product.product'].sudo().browse(int(data['id'])).list_price
