# -*- coding: utf-8 -*-
{
    'name': "stock_spacefill",
 
    'summary': """
       SpaceFill connector""",

    'description': """
        Synchronize Odoo with SpaceFill
    """,

    'author': "irokoo",
    'website': "http://www.irokoo.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',
    'licence': 'GPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_stock','delivery','purchase','sale'],

    # always loaded
    'data': [
        # DATA
        'data/ir_cron.xml',
        # SECURITY
        'security/security.xml',
        'security/ir.model.access.csv',
        # VIEWS
        'views/product_template.xml',
        'views/product_view.xml',
        'views/spacefill_statut.xml',
        'views/spacefill.xml',
        'views/spacefill_menu.xml',
        'views/stock_package_type_view.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_picking_view.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "active": True,
    "installable": True,
}
