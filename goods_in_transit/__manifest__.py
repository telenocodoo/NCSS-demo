# -*- coding: utf-8 -*-
{
    'name': 'goods_transit',
    'version': '13.0.1',
    'summary': 'goods_transit',
    'category': 'goods_transit',
    'author': 'Magdy,TeleNoc',
    'description': """
    goods_transit
    """,
    'depends': ['base', 'mail', 'purchase', 'stock', 'purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/goods_transit.xml',
    ]
}
