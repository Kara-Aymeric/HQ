# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_exported = fields.Boolean(default=False, string='SPACEFILL')
    spacefill_warehouse_account_id = fields.Char(string='ID WAREHOUSE')
