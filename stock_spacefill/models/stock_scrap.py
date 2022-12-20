# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.constrains('location_id')
    def _constrains_exported_location_id(self):
        '''
            Check if user can dispose
        '''
        for scrap in self:
            if scrap.location_id.warehouse_id and scrap.location_id.warehouse_id.is_exported \
                    and not self.user_has_groups('stock_spacefill.group_spacefill_connector_users'):
                raise UserError(_('You are not allowed to scrap for this warehouse !'))
