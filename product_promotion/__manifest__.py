# -*- coding: utf-8 -*-
{
    'name': "Promotion sur article",
    'summary': """
        Le module propose de configurer une période de promotion au niveau de la configuration d'un article. 
        La promotion sera alors appliquée à la ligne de vente lors de la saisie d'un devis.
    """,
    'description': """ """,
    'author': "HENNION Kévin",
    'website': "https://hennet-solutions.fr",
    'category': 'Sales/Sales',
    'version': '15.0.22.11.16',
    'license': "LGPL-3",
    'installable': True,
    'depends': ['base', 'sale'],
    'data': [
        'data/product_template_cron.xml',
        'report/sale_report_templates.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/res_company_views.xml',
        'views/sale_order_views.xml',
    ],
}
