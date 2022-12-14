# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed')], string="Discount type")
    discount_product = fields.Float(string="Discount / Product", digits="Discount", default=0.0,
                                    help="The discount is percentage or fixed depending "
                                         "on the configuration of the article.")
    total_discount = fields.Monetary(string="Total discount")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_type', 'discount_product')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        Sending the new unit price in order to calculate the subtotal. Displays the base unit price in the form
        """
        vals = {}
        for line in self.filtered(lambda l: l.discount_product and l.order_id.state not in ["done", "cancel"]):
            discounted_price_unit = 0
            if line.discount_type == 'percentage':
                discounted_price_unit = line.price_unit * (1 - (line.discount_product or 0.0) / 100.0)
            elif line.discount_type == 'fixed':
                discounted_price_unit = line.price_unit - (line.discount_product or 0.0)
            line.total_discount = (line.price_unit - discounted_price_unit) * line.product_uom_qty

            # Stores unit price
            vals[line] = {
                "price_unit": line.price_unit,
            }
            line.update({"price_unit": discounted_price_unit})

        res = super(SaleOrderLine, self)._compute_amount()
        # After calculating the discounted subtotal, the base unit price is displayed in the sale form
        for line in vals.keys():
            line.update(vals[line])

        return res

    @api.onchange('product_id')
    def _onchange_discount_product_id(self):
        """ Get the discount on the product if it exists """
        if self.product_id:
            product_id = self.product_id
            if product_id.is_promotion and product_id.discount > 0.0:
                if product_id.begin_date <= datetime.date.today() <= product_id.end_date:
                    self.discount_type = product_id.discount_type
                    if product_id.discount_type == "percentage":
                        self.discount_product = product_id.percentage_value
                    elif product_id.discount_type == "fixed":
                        self.discount_product = product_id.discount

    # def _prepare_invoice_line(self, **kwargs):
    #     res = super()._prepare_invoice_line(**kwargs)
    #     res.update({"discount_product": self.discount_product})
    #     return res
