# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from datetime import date, datetime

class SpacefillConfig(models.Model):
    _name = "spacefill.config"
    _description = "spacefill.config"

    spacefill_lsp_token = fields.Char(string='Token LSP')
    spacefill_shipper_token = fields.Char(string='Token Shipper')
    spacefill_api_url = fields.Char(string='URL SPACEFILL')
    spacefill_erp_account_id =fields.Char(string='ID ERP Shipper')
    spacefill_delay = fields.Integer("Délai prévenance en h")
    spacefill_confirm_schedule = fields.Boolean("Warehouse need to confirm scheduling",default=False)