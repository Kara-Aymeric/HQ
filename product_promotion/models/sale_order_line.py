import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_fixed = fields.Float(string="Fixed discount", digits="Discount", default=0.0,
                                  help="Fixed discount on the product based on the Unit Price")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_fixed')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        Sending the new unit price in order to calculate the subtotal. Displays the base unit price in the form
        """
        vals = {}
        for line in self.filtered(lambda l: l.discount_fixed and l.order_id.state not in ["done", "cancel"]):
            discounted_price_unit = line.price_unit - (line.discount_fixed or 0.0)
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

    @api.constrains('discount', 'discount_fixed')
    def _check_if_one_discount(self):
        """ Check if only one discount is applied """
        for line in self:
            if line.discount and line.discount_fixed:
                raise ValidationError(_("Une seule remise par ligne d'article est possible. ""Merci de modifier"))

    @api.onchange('discount')
    def _onchange_discount_percent(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('discount_fixed')
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.onchange('product_id')
    def _onchange_discount_product_id(self):
        """ Get the discount on the product if it exists """
        if self.product_id:
            product_id = self.product_id
            if product_id.is_promotion and product_id.discount > 0.0:
                if product_id.begin_date <= datetime.date.today() <= product_id.end_date:
                    if product_id.discount_type == "percentage":
                        self.discount = product_id.percentage_value
                    elif product_id.discount_type == "fixed":
                        self.discount_fixed = product_id.discount

    # def _prepare_invoice_line(self, **kwargs):
    #     res = super()._prepare_invoice_line(**kwargs)
    #     res.update({"discount_fixed": self.discount_fixed})
    #     return res
