from odoo import api, fields, models, _


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    spacefill_manage_only = fields.Boolean(string='Manage only by Spacefill ?')

    