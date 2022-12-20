# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

def write(self,vals):
    res=super(StockMove, self).write(vals)
 
    return res