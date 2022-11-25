# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductPromotion(models.Model):
    _name = 'product.promotion'
    _description = 'Promotion history. No impact on related articles and models'
    _order = 'id desc'

    product_template_id = fields.Many2one('product.template', string="Product template",
                                          help="Product template associated with the promotion")
    begin_date = fields.Date(string="Begin date")
    end_date = fields.Date(string="End date")
    discount_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed')], string="Discount type")
    percentage_value = fields.Float(string="Percentage value",
                                    help="Value used to calculate the discount on the product")
    discount = fields.Float(string="Product discount", store=True, compute="_compute_discount",
                            help="Discount value calculated automatically if discount type is percentage")
