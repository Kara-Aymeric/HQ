# -*- coding: utf-8 -*-
#############################################################################


##############################################################################

from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = "sale.order" 

    def action_confirm(self):
        res= super(SaleOrder, self).action_confirm() 
        for order in self:
            pickings = self.env['stock.picking'].search([('origin','=',order.name)])
            for picking in pickings:
                if picking.picking_type_id.warehouse_id.is_exported:
                    #picking.export_order_exit_to_spacefill()
                    self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True})
        return res

    def update_exit(self):
        import pdb
        #pdb.set_trace()
        pickings = self.env['stock.picking'].search(
           [('origin', '=', self.name)])
        for picking in pickings:
            if picking.picking_type_id.warehouse_id.is_exported:
                picking.export_order_exit_to_spacefill()
   
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        pickings = self.env['stock.picking'].search(
           [('origin', '=', self.name)])
        if self.name:
            pickings = self.env['stock.picking'].search([('origin', '=', self.name)])  
            for picking in pickings:                  
                if picking.picking_type_id.warehouse_id.is_exported:
                    if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                        picking_id = self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True})                 
                #picking.export_order_entry_to_spacefill()
        return res
    