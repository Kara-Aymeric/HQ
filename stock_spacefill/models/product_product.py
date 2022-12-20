
import logging
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.stock_spacefill.spacefillpy.api import API as API

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_exported=fields.Boolean('Spacefill Product', copy=False)
    item_spacefill_id=fields.Char('Spacefill id item', copy=False)



    def create_spacefill_variant(self,instance,vals):
        """
        Create or update a variant in spacefill

        Args:
            instance (obj): instance of spacefill
            vals (dict): values of the variant
        """
        item_url = 'logistic_management/master_items/'
        #if self._constrains_mandatory_fields():
       
        res= instance.create(instance.url+item_url, vals)
        if res:
                if not self.item_spacefill_id:
                        self.message_post(
                                                body=_('Created item in Spacefill with id %s') % (res.get('id')),
                                                )
                        self.write({'item_spacefill_id' : res.get('id')})
                        self.write({'is_exported': True})
                else:
                        self.message_post(
                                                body=_('Updated item in Spacefill with id %s') % (res.get('id')),
                                                )
                       
    def export_product_in_spacefill(self):
        """
            Export product in spacefill
        """
        for product in self:
            if not product.item_spacefill_id:
                instance, setup = product.get_instance_spacefill()
                spacefill_mapping= {
                    "shipper_account_id": setup.spacefill_erp_account_id,
                    "item_reference": product.default_code,
                    "designation": product.name,
                    "cardboard_box_quantity_by_pallet": None,
                    "each_barcode_type": "EAN",
                    "each_barcode": product.barcode if product.barcode else None,
                    "cardboard_box_barcode_type": "EAN",
                    "cardboard_box_barcode": None,
                    "pallet_barcode_type": "EAN",
                    "pallet_barcode": None,
                    "each_quantity_by_cardboard_box": None,
                    "each_quantity_by_pallet":None,
                    "each_is_stackable": "true",
                    "cardboard_box_is_stackable": "false",
                    "pallet_is_stackable": "false",
                    "each_width_in_cm": None,
                    "each_length_in_cm": None,
                    "each_height_in_cm": None,
                    "each_volume_in_cm3": None,
                    "cardboard_box_width_in_cm": None,
                    "cardboard_box_length_in_cm": None,
                    "cardboard_box_height_in_cm": None,
                    "cardboard_box_volume_in_cm3": None,
                    "pallet_width_in_cm": None,
                    "pallet_length_in_cm": None,
                    "pallet_height_in_cm": None,
                    "pallet_gross_weight_in_kg": None,
                    "pallet_net_weight_in_kg": None,
                    "cardboard_box_gross_weight_in_kg": None,
                    "cardboard_box_net_weight_in_kg": None,
                    "each_gross_weight_in_kg": product.weight if product.weight else None,
                    "each_net_weight_in_kg": product.weight if product.weight else None,
                    "edi_erp_id": product.id,
                    "edi_wms_id": None,
                    "edi_tms_id": None,
                    "transfered_to_erp_at": None,
                    "transfered_to_wms_at": None,
                    "transfered_to_tms_at": None,
                    }
                vals = product.prepare_dict_vals(spacefill_mapping)
                product.create_spacefill_variant(instance,vals)

    def get_instance_spacefill(self):
        setup = self.env['spacefill.config'].search([])
        instance = API(setup.spacefill_api_url,
                       setup.spacefill_shipper_token)       
        return instance,setup

    def get_odoo_packaging(self ):
        values = {}
        values["cardBoardBox"] = self.env['product.packaging'].search([('is_spacefill_cardboard_box', '=', True), ('product_id', '=', self.id)])
        values["pallet"] = self.env['product.packaging'].search([('is_spacefill_pallet', '=', True ), ('product_id', '=', self.id)])
        return values
        
    def prepare_dict_vals(self, spacefill_mapping):
        spacefill_cardboard_box = False
        spacefill_pallet = False
        if self.packaging_ids:
            for package in self.packaging_ids:
                if package.package_type_id.is_spacefill_cardboard_box:
                    spacefill_cardboard_box = True
                    obj_cardbox= package

                elif package.package_type_id.is_spacefill_pallet:
                    spacefill_pallet = True
                    obj_pal = package

            
            if spacefill_pallet:
                if spacefill_cardboard_box:
                    if obj_pal.qty % obj_cardbox.qty == 0:
                        spacefill_mapping["cardboard_box_quantity_by_pallet"] = int(obj_pal.qty//obj_cardbox.qty)
                    else:
                        self.message_post(
                                                body=_('Cardboard box quantity by pallet is not an integer'),
                                                )               
                    
                else:
                    spacefill_mapping["each_quantity_by_pallet"] = int(obj_pal.qty)

                spacefill_mapping["pallet_barcode"] = obj_pal.package_type_id.barcode
                spacefill_mapping["pallet_width_in_cm"] = obj_pal.package_type_id.width
                spacefill_mapping["pallet_length_in_cm"] = obj_pal.package_type_id.packaging_length
                spacefill_mapping["pallet_height_in_cm"] = obj_pal.package_type_id.height
                spacefill_mapping["pallet_gross_weight_in_kg"] = obj_pal.package_type_id.gross_weight
                spacefill_mapping["pallet_net_weight_in_kg"] = obj_pal.package_type_id.gross_weight

            if spacefill_cardboard_box:
                # remplir les détails cardboard box
                #cardBoardBox = values["cardBoardBox"]
                spacefill_mapping["each_quantity_by_cardboard_box"] = int(obj_cardbox.qty)
                spacefill_mapping["cardboard_box_barcode"] = obj_cardbox.package_type_id.barcode
                spacefill_mapping["cardboard_box_width_in_cm"] = obj_cardbox.package_type_id.width
                spacefill_mapping["cardboard_box_length_in_cm"] = obj_cardbox.package_type_id.packaging_length
                spacefill_mapping["cardboard_box_height_in_cm"] = obj_cardbox.package_type_id.height
                spacefill_mapping["cardboard_box_gross_weight_in_kg"] = obj_cardbox.package_type_id.gross_weight
                spacefill_mapping["cardboard_box_net_weight_in_kg"] = obj_cardbox.package_type_id.gross_weight

            
        return spacefill_mapping

    def get_values(self, vals):

        for product in self:
            if product.weight:
                vals['each_gross_weight_in_kg'] = product.weight 
                vals['each_net_weight_in_kg'] = product.weight 

            if not product.default_code: 
                ref = product.name
                for attribute_value in self.product_template_attribute_value_ids:
                    tmpValue = attribute_value.name
                    ref += "" + attribute_value.attribute_id.name[0].upper() + tmpValue
                    self.write({'default_code' : ref})
                    vals['item_reference'] = ref
            else:
                vals['item_reference'] = product.default_code

            return vals
    
    def cron_update_inventory(self):
        """
            import product inventories from spacefill warehouse to odoo warehouse
        """
        products =self.search([('is_exported', '=', True ), ('item_spacefill_id', '!=', None)])
        for product in products:
            product.create_inventory_from_spacefill()
    
    def create_inventory_from_spacefill(self):
        import pdb
        #pdb.set_trace()
        instance, setup = self.get_instance_spacefill()
        item_url = 'logistic_management/master_items/'+ self.item_spacefill_id +'/'
        list={}
        vals= instance.browse(instance.url+item_url,list)
        if vals.get('stock_by_warehouse'):
            for warehouse_id in vals.get('stock_by_warehouse'):
                if warehouse_id.get("each_actual_quantity") >= 0:
                    warehouse = self.env['stock.warehouse'].search(
                                        [('company_id', '=', self.env.company.id),('spacefill_warehouse_account_id' ,'=',warehouse_id.get("warehouse_id"))], limit=1)
                    inventories= self.env['stock.quant'].with_context(inventory_mode=True).create({
                                                                                'product_id': self.id,
                                                                                'location_id': warehouse.lot_stock_id.id,
                                                                                'inventory_quantity': float(warehouse_id.get("number_of_eaches")),                                                                                
                                                                            }).action_apply_inventory()
                    
                    #elf.env['stock.quant'].action_apply_inventory()'lot_name': lot2.id,
                #lot_id': Lot.create({'name': 'S3', 'product_id': consumed_serial.id, 'company_id': self.env.company.id}).id

        return True
    
    def create_inventory_from_spacefill_with_lot(self):
        import pdb
        #pdb.set_trace()
        instance, setup = self.get_instance_spacefill()
        item_url = 'logistic_management/pallet-ssccs/'#+ self.item_spacefill_id +'/'
        filter={'master_item_id':self.item_spacefill_id,
                'limit':1000,},
        vals= instance.search_read(instance.url+item_url,filter)

        for line in vals:
            if line.get("each_actual_quantity") >= 0:
                    warehouse = self.env['stock.warehouse'].search(
                                        [('company_id', '=', self.env.company.id),('spacefill_warehouse_account_id' ,'=',line.get("warehouse_id"))], limit=1)
                    if warehouse:
                        inventories= self.env['stock.quant'].with_context(inventory_mode=True).create({
                                                                                'product_id': self.id,
                                                                                'lot_name': line.get("batch_name"),
                                                                                'location_id': warehouse.lot_stock_id.id,
                                                                                'inventory_quantity': float(line.get("each_actual_quantity")),                                                                                
                                                                            }).action_apply_inventory()
                    
                    #elf.env['stock.quant'].action_apply_inventory()'lot_name': lot2.id,
                #lot_id': Lot.create({'name': 'S3', 'product_id': consumed_serial.id, 'company_id': self.env.company.id}).id

        return True
    #CRUDS 
    def write(self, vals):
        if 'default_code' in vals:
            for product in self.filtered(lambda p: p.is_exported and p.item_spacefill_id):
                if product.default_code != vals['default_code']:
                    raise UserError(_("You can't change the reference of the product, if this product is exported in Spacefill"))
        return super(ProductProduct, self).write(vals)

    def _constrains_mandatory_fields(self):
        '''
            Check that the fields are sent correctly
        '''
        MANDATORY_FIELDS = ['default_code', 'barcode', 'detailed_type', 'weight']
        for product in self:
            for field in MANDATORY_FIELDS:
                if field == 'detail_type':
                    if product.detailed_type != 'product':
                        raise ValidationError(_('The detailed type must be product'))
                if not product[field]:
                    raise ValidationError(_('The field %s is mandatory.', field))


 