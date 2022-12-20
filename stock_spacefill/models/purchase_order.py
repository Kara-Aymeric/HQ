# -*- coding: utf-8 -*-
#############################################################################

#
##############################################################################

from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from dateutil.relativedelta import relativedelta
from datetime import date, datetime


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        pickings = self.env['stock.picking'].search(
           [('origin', '=', self.name)])
        for picking in pickings:
            if picking.picking_type_id.warehouse_id.is_exported:
            #picking.export_order_entry_to_spacefill()
                self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True})
        return res

  
    def update_entry(self):
        import pdb
        #pdb.set_trace()
        pickings = self.env['stock.picking'].search(
           [('origin', '=', self.name)])
        for picking in pickings:
            if picking.picking_type_id.warehouse_id.is_exported:
                picking.export_order_entry_to_spacefill()
    
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if self.name:
            pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
            for picking in pickings:                    
                if picking.picking_type_id.warehouse_id.is_exported:
                    if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                        picking_id = self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True})
                    #picking.export_order_entry_to_spacefill()
        return res
      