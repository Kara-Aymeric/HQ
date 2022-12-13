# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_discount = fields.Monetary(string='Discount total', store=True, readonly=True,
                                      default=0.0, tracking=True, compute="_compute_amount_discount")

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        """ Recompute taxes """
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            if order_line.discount_type == 'percentage':
                price = order_line.price_unit * (1 - (order_line.discount_product or 0.0) / 100.0)
            elif order_line.discount_type == 'fixed':
                price = order_line.price_unit - (order_line.discount_product or 0.0)

            order = order_line.order_id
            return order_line.tax_id._origin.compute_all(
                price,
                order.currency_id,
                order_line.product_uom_qty,
                product=order_line.product_id,
                partner=order.partner_shipping_id
            )

        res = super()._compute_tax_totals_json()
        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)
        return res

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        Calculates the total amount discounted based on the discount on the unit price of the item.
        This calculation is for information only and has no impact on the Odoo standard
        """
        res = super(SaleOrder, self)._amount_all()
        for order in self:
            amount_discount = 0.0
            for line in order.order_line:
                amount_discount += line.total_discount
            order.amount_discount = amount_discount
        return res
