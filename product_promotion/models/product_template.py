# -*- coding: utf-8 -*-
import datetime
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_promotion = fields.Boolean(string="Is on promotion")
    product_promotion_ids = fields.One2many('product.promotion', 'product_template_id', string='Promotions')
    company_accepts_promotion = fields.Boolean(string="The company accepts promotions",
                                               related="company_id.accept_promotion")

    # Discount declare part
    begin_date = fields.Date(string="Begin date", tracking=True)
    end_date = fields.Date(string="End date", tracking=True)
    discount_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed')], string="Discount type", tracking=True)
    percentage_value = fields.Float(string="Percentage value",
                                    help="Value used to calculate the discount on the product", tracking=True)
    discount = fields.Float(string="Product discount", store=True, compute="_compute_discount",
                            help="Discount value calculated automatically if discount type is percentage",
                            tracking=True)
    new_price = fields.Float(string="Discounted sale price", store=True, compute="_compute_new_price",
                             help="New sale price by applying the discount on the product", tracking=True)

    warning_discount_info = fields.Char(string="Information", store=False, copy=False)

    @api.depends('discount_type', 'percentage_value', 'list_price')
    def _compute_discount(self):
        for rec in self:
            if rec.is_promotion:
                if rec.discount_type == 'percentage' and rec.percentage_value > 0:
                    rec.discount = (rec.percentage_value/100) * rec.list_price
            else:
                rec.discount = 0

    @api.depends('discount')
    def _compute_new_price(self):
        for rec in self:
            if rec.is_promotion:
                rec.new_price = rec.list_price - rec.discount
            else:
                rec.new_price = 0

    @api.constrains('begin_date', 'end_date')
    def _check_promotion_date(self):
        """ Allows you to check if the promotion start date is earlier than the end date """
        for record in self:
            if record.begin_date > record.end_date:
                raise ValidationError('La date de début de la promotion est supérieure à la date de fin de la '
                                      'promotion. Veuillez vérifier ces informations.')

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        if self.discount_type and not self.is_promotion:
            self.is_promotion = True

    @api.onchange('discount_type', 'list_price', 'taxes_id', 'discount', 'begin_date', 'end_date')
    def _onchange_warning_discount_info(self):
        if self.is_promotion:
            self.warning_discount_info = "Une promotion sur l'article est configurée. " \
                                         "Merci de vérifier avant de sauvegarder."

    @api.onchange('is_promotion')
    def _onchange_is_promotion(self):
        if not self.is_promotion and self.discount_type:
            self.write({
                'begin_date': False,
                'end_date': False,
                'discount_type': False,
                'percentage_value': 0,
                'discount': 0,
                'new_price': 0,
                'warning_discount_info': "Une promotion sur l'article était configurée. "
                                         "Merci de vérifier avant de sauvegarder.",
            })

    def _cron_update_discount(self):
        """ This cron will :
          - deactivate the promotion if the date has passed
          - cleans the fields concerning the promotion
        """
        product_template_ids = self.search([('is_promotion', '=', True), ('end_date', '<', datetime.date.today())])
        for record in product_template_ids:
            record.write({
                'is_promotion': False,
                'begin_date': False,
                'end_date': False,
                'discount_type': False,
                'percentage_value': 0,
                'discount': 0,
                'new_price': 0,
            })
            _logger.info(f"Promotion sur l'article [{record.name}] dont l'identifiant est [{record.id}] désactivée")

    @api.model
    def create(self, values):
        """ Overwrite create method """
        record = super(ProductTemplate, self).create(values)
        if values.get('is_promotion'):
            if record.discount > 0:
                vals = {
                    'product_template_id': record.id,
                    'begin_date': record.begin_date,
                    'end_date': record.end_date,
                    'discount_type': record.discount_type,
                    'percentage_value': record.percentage_value,
                    'discount': record.discount,
                }
                record.product_promotion_ids.create(vals)

        return record

    def write(self, values):
        """ Overwrite write method """
        res = super(ProductTemplate, self).write(values)
        if values.get('is_promotion') or values.get('begin_date') or values.get('end_date') \
                or values.get('discount_type') or values.get('percentage_value') \
                or values.get('percentage_value') or values.get('discount'):
            for product in self:
                if product.discount > 0:
                    vals = {
                        'product_template_id': product.id,
                        'begin_date': product.begin_date,
                        'end_date': product.end_date,
                        'discount_type': product.discount_type,
                        'percentage_value': product.percentage_value,
                        'discount': product.discount,
                    }
                    product.product_promotion_ids.create(vals)

        return res
