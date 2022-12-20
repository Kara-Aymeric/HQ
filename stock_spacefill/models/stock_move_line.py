# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

def write(self,vals):
    res=super(StockMoveLine, self).write(vals)
    
    if self.picking_id.picking_type_id.warehouse_id.is_exported and self.env.context.get('_send_on_write')!='NO':
        if not self.env['spacefill.update'].search([('id_to_update','=',self.picking_id.id),('is_to_update','=',True)]):
            self.env['spacefill.update'].create({'id_to_update':self.picking_id.id,'is_to_update':True})
        
    return res