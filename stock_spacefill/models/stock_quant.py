# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.constrains('location_id')
    def _constrains_exported_location_id(self):
        '''
            Check if current user is allowed to create inventories for exported locations.
        '''
        for inventory in self:
            if inventory.location_id.warehouse_id and inventory.location_id.warehouse_id.is_exported \
                    and not self.user_has_groups('stock_spacefill.group_spacefill_connector_users'):
                raise UserError(_('You are not allowed to make inventory for this location !'))
