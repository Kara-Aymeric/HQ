from odoo import models, fields, _


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    gross_weight = fields.Float(
        'gross weight', help='gross weight shippable in this packaging')
    is_spacefill_cardboard_box = fields.Boolean('SpaceFill CardBoard Box',
        default=False)
    is_spacefill_pallet = fields.Boolean('SpaceFill Pallet', default=False)