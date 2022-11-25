# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    accept_promotion = fields.Boolean(string="Allows to use the promotion module on product")

