from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_discount = fields.Monetary(string='Discount total', store=True, readonly=True,
                                      default=0.0, tracking=True, compute="_compute_amount_discount")

    @api.depends('order_line.price_total')
    def _compute_amount_discount(self):
        """
        Calculates the total amount discounted based on the discount on the unit price of the item.
        This calculation is for information only and has no impact on the Odoo standard
        """
        for order in self:
            amount_discount = 0.0
            for line in order.order_line:
                discounted_price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0) - \
                                        (line.discount_fixed or 0.0)
                diff = line.price_unit - discounted_price_unit
                total_discount = line.product_uom_qty * diff
                amount_discount += total_discount
            order.amount_discount = amount_discount
