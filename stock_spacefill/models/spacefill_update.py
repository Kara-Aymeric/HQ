# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SpacefillUpdate(models.Model):
    _name = "spacefill.update"
    _description = "spacefill.update"


    id_to_update = fields.Char(string='Picking id')
    is_to_update =fields.Boolean(string='Is to update ?',default=False)

    def update(self):
        #import pdb;pdb.set_trace()
        ids_to_treat =self.search([('is_to_update','=',True)])
        for id in ids_to_treat:
            picking = self.env['stock.picking'].search([('id','=',id.id_to_update)])
            if picking.picking_type_id.warehouse_id.is_exported:
                picking.action_server_synchronize_order()
                id.is_to_update = False
    def delete(self):
        ids_to_treat =self.search([])
        import pdb;pdb.set_trace()
        for id in ids_to_treat:
            id.delete()