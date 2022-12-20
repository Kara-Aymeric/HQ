from odoo import models, fields, api, exceptions, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def update_spacefill(self, instance, vals):
        item_url = 'logistic_management/master_items/' + self.item_spacefill_id + '/'

        res = instance.update(instance.url+item_url, vals)
       # self.write({'item_spacefill_id': res.get('id')})

    def export_product_tmpl_in_spacefill(self):
        for product in self:
            for variant in product.product_variant_ids:
                variant.export_product_in_spacefill()

    def get_instance_spacefill(self):
        setup = self.env['spacefill.config'].search([])
        instance = API(setup.spacefill_api_url,
                       setup.spacefill_shipper_token)
        return instance, setup

    def get_odoo_packaging(self ):
        values = {}
        values["cardBoardBox"] = self.env['product.packaging'].search([('is_spacefill_cardboard_box', '=', True), ('product_id', '=', self.id)])
        values["pallet"] = self.env['product.packaging'].search([('is_spacefill_pallet', '=', True ), ('product_id', '=', self.id)])

        return values