from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

# to do : add a field to know if the picking is already exported to spacefill, and if yes, don't export it again
# to do : if another picking is created , check if one exist, if yes the first one must be in canceled state other case  don't create it
# todo : if the order is canceled, the picking must be canceled too
# todo if check status is false and picking id exitst  in spacefill.update the put the id to update at false

class StockPicking(models.Model):
    _inherit = "stock.picking"

    order_spacefill_id = fields.Char('order ID spacefill')
    status_spacefill = fields.Char('order spacefill status')
    

    # GET METHODS
    
    def get_instance_spacefill(self):
        setup = self.env['spacefill.config'].search([])
        instance = API(setup.spacefill_api_url,
                       setup.spacefill_shipper_token)        
        return instance,setup

    def cron_maj_status(self):
        pickings = self.env['stock.picking'].search([
                            ('order_spacefill_id', '!=', False),
                            ('state','not in',['done','cancel']),                           
                         
                ])
        for picking in pickings:
            picking.update_status_spacefill()
    
    def action_server_synchronize_order(self):
        for picking in self:
                if picking.picking_type_id.warehouse_id.is_exported: # and self.env.context.get('_send_on_write')!='NO':

                        if picking.picking_type_code == 'incoming':            
                            picking.export_order_entry_to_spacefill()

                        elif picking.picking_type_code == 'outgoing':                                     
                            picking.export_order_exit_to_spacefill()
                                            
                        elif picking.picking_type_code == 'internal':
                                             picking.message_post(
                                            body=_('Internal trasnfert is not allowed for Spacefill warehouse') 
                                            )
                                  
                           
    def check_spacefill_status(self):
        url = "logistic_management/orders/"
        spacefill_instance, setup = self.get_instance_spacefill()
        data = spacefill_instance.browse(setup.spacefill_api_url + url + str(self.order_spacefill_id) + '/')
        spacefill_statut = self.env['spacefill.statut'].search([('spacefill_statut', '=', data.get('status'))])
        if spacefill_statut.is_ok_to_update:
            return True
        else:
            self.message_post(
                            _boydy=_('Update is not allowed at this step'))
            res=  self.env['spacefill.update'].search([('id_to_update','=',self.id),('is_to_update','=',True)])
            if res:
                res.is_to_update=False    


    # CRUD METHODS
    def update_status_spacefill(self):
        url = "logistic_management/orders/"
        filter={}
        config = self.env['spacefill.config'].search([], limit=1)
        spacefill_instance, setup = self.get_instance_spacefill()     
        data = spacefill_instance.browse(setup.spacefill_api_url + url + str(self.order_spacefill_id) + '/')
        spacefill_statut = self.env['spacefill.statut'].search([('spacefill_statut', '=', data.get('status'))])
        # _logger.info("data %r", data)
        if spacefill_statut:
            self.env.context.get('_send_on_write') == 'NO'
            self.write({'status_spacefill': spacefill_statut.spacefill_statut})
            if spacefill_statut.is_default_done and self.state != 'done':
                for line in data.get('order_items'):
                    product = self.env['product.product'].search([('item_spacefill_id', '=', line.get('master_item_id'))], limit=1)
                    line_id = False
                    if product:
                        line_id = self.env['stock.move.line'].search([('picking_id','=',int(data.get('edi_erp_id'))),('product_id','=',product.id)])
                        if line_id:
                            line_id.write({'qty_done': int(line.get('actual_quantity'))})

                self.with_context(skip_backorder=True, picking_ids_not_to_backorder=self.ids).button_validate()
                """ 'effective_executed_at': '2022-10-26T11:00:00+00:00'"""
                date_effective = data.get('effective_executed_at')
                if date_effective:
                    date_effective = datetime.strptime(date_effective[:19].replace('T',' '), '%Y-%m-%d %H:%M:%S')
                    self.write({'date_done': date_effective})

            if spacefill_statut.is_default_cancel:
               # nothinhg to do

               return True
        return True

    def update_status_spacefill_with_lot(self):
        url = "logistic_management/orders/"
        filter={}
        config = self.env['spacefill.config'].search([], limit=1)
        spacefill_instance, setup = self.get_instance_spacefill()     
        data = spacefill_instance.browse(setup.spacefill_api_url + url + str(self.order_spacefill_id) + '/')
        spacefill_statut = self.env['spacefill.statut'].search([('spacefill_statut', '=', data.get('status'))])
        # _logger.info("data %r", data)
        if spacefill_statut:
            self.env.context.get('_send_on_write') == 'NO'
            self.write({'status_spacefill': spacefill_statut.spacefill_statut})
            if spacefill_statut.is_default_done and self.state != 'done':
                for line in data.get('order_items'):
                    product = self.env['product.product'].search([('item_spacefill_id', '=', line.get('master_item_id'))], limit=1)                    
                    line_id = False
                    if product:
                        if line.get('batch_name'):
                            lot = self.env['stock.production.lot'].search([('name', '=', line.get('batch_name')),('product_id','=',product.id)], limit=1)
                            if lot:
                                line_id = self.env['stock.move.line'].search([('picking_id','=',int(data.get('edi_erp_id'))),('product_id','=',product.id),('lot_id','=',lot.id)])
                                if not line_id:
                                    self.create_new_line(self, line, product,lot)
                                else:
                                    line_id.write({'qty_done': int(line.get('actual_quantity'))})
                                    line_id.write({'lot_id': lot.id})
                            else:
                                lot_id = self.env['stock.production.lot'].create({
                                                                                            'name': line['lot_name'],
                                                                                            'company_id': self.company_id.id,
                                                                                            'product_id': product.id
                                                                                        })
                                self.create_new_line(self, line, product, lot)
                        else:
                            line_id = self.env['stock.move.line'].search([('picking_id','=',int(data.get('edi_erp_id'))),('product_id','=',product.id)])
                            line_id.write({'qty_done': int(line.get('actual_quantity'))})
                            

                self.with_context(skip_backorder=True, picking_ids_not_to_backorder=self.ids).button_validate()
                """ 'effective_executed_at': '2022-10-26T11:00:00+00:00'"""
                date_effective = data.get('effective_executed_at')
                if date_effective:
                    date_effective = datetime.strptime(date_effective[:19].replace('T',' '), '%Y-%m-%d %H:%M:%S')
                    self.write({'date_done': date_effective})

            if spacefill_statut.is_default_cancel:
               # nothinhg to do

               return True
        return True

    def create_new_line(self, line, product,lot):
        """
        Create a new line in the picking
        """
        StockMoveLine = self.env['stock.move.line']
        move_line_id = StockMoveLine.create({
            'picking_id': self.id,
            'product_id': product.id,
            'qty_done': line.get('actual_quantity', 0),
            'lot_id': lot.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'product_uom_id': product.uom_id.id,
        })
        # new_move = self.env['stock.move'].create(move_line_id._prepare_stock_move_vals())
        # move_line_id.move_id = new_move.id
        return move_line_id


    def create(self,vals):
        # protect only one picking per sale ou purchase order 

        return super(StockPicking,self).create(vals)

    def write(self,vals):         
        import pdb
       # pdb.set_trace()  
        res=super(StockPicking, self).write(vals)
        for picking in self:
            if picking.picking_type_id.warehouse_id.is_exported and self.env.context.get('_send_on_write')!='NO' and picking.state not in ['done','cancel']:
                if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                    self.env['spacefill.update'].create({'id_to_update':picking.id,'is_to_update':True})
   
        return res

    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        for picking in self:
            if picking.picking_type_id.warehouse_id.is_exported:
                if picking.check_spacefill_status():
                    picking.export_order_cancel_to_spacefill() 
        return res

    
    def export_order_cancel_to_spacefill(self):
        url = "/logistic_management/orders" #/{order_id}/shipper_cancels_order_action/"
        spacefill_instance, setup = self.get_instance_spacefill()
        res = spacefill_instance.call(setup.spacefill_api_url + url + str(self.order_spacefill_id) + '/shipper_cancels_order_action/')
        if res:
                    self.message_post(
                                    body=_('Order %s is Canceled to Spacefill' ) % self.order_spacefill_id
                                    )
        else:
                raise UserError(
                        _('Error from API : %s') % res.text)
   
    
    def check_spacefill_wrkflw(self):
        # update status
        return True
    
    def export_order_entry_to_spacefill(self):
        
        instance, setup = self.get_instance_spacefill()
        self.create_or_update_spacefill(instance, setup,'ENTRY')

        return True
    def export_order_exit_to_spacefill(self):
        instance, setup = self.get_instance_spacefill()
        self.create_or_update_spacefill(instance, setup,'EXIT')
        return True
    
    def create_or_update_spacefill(self, instance, setup,type):
        
        order_items = []
        import pdb
        #pdb.set_trace()
        """Verification de la date prévue en fonction du délai de prévenance"""
        delay = setup.spacefill_delay or 24
        date_delay = fields.Datetime.from_string(fields.Datetime.now())\
                   + relativedelta(hours=delay)
        if self.scheduled_date < date_delay:
            scheduled_date = date_delay
        else:
            scheduled_date = self.scheduled_date
        if type =='ENTRY':
            order_values = self.prepare_entry_vals(scheduled_date)
            item_url = 'logistic_management/orders/entry/'
        else:
            order_values = self.prepare_exit_vals(scheduled_date)
            item_url = 'logistic_management/orders/exit/'

        for line in self.move_line_ids:
            order_lines_values = {}
            import pdb
            #pdb.set_trace()
            # need to update with id space fill on response
            if line.product_uom_qty > 0:
                order_lines_values['master_item_id'] = line.product_id.item_spacefill_id
                # self.get_item_packaging_type(item)
                order_lines_values["item_packaging_type"] = "EACH"
                order_lines_values["expected_quantity"] = line.product_uom_qty
                if line.lot_name: #and line.get('lot_name'):
                    """"
                            lot_id = self.env['stock.production.lot'].search([
                                ('name', '=', line['lot_name']),
                                ('product_id', '=', line.product_id.id)
                            ])
                            if not lot_id:
                                lot_id = self.env['stock.production.lot'].create({
                                    'name': line['lot_name'],
                                    'company_id': self.company_id.id,
                                    'product_id': line.product_id.id
                                })
                    """
                    order_lines_values['batch_name'] = line.lot_name
                order_items.append(
                    order_lines_values
                    )
            order_values.update({"order_items": order_items})
        if self.order_spacefill_id and self.check_spacefill_status():
            item_url ='logistic_management/orders/'+self.order_spacefill_id+'/shipper_updates_order_action'
            res = instance.call('POST',instance.url+item_url, order_values)
            if res:
                self.message_post(
                                    body=_('Order %s is updated to Spacefill' ) % self.order_spacefill_id
                                    )
            else:
                raise UserError(
                        _('Error from API : %s') % res.text)
            
        else:
            if not self.order_spacefill_id :
                res = instance.create(instance.url+item_url, order_values)
                self = self.with_context(
                _send_on_write="NO")    
                if res:
                    self.write({'order_spacefill_id': res.get('id')})
                    self.write({'status_spacefill': res.get('status')})
                    self.message_post(
                                        body=_('Order is created to Spacefill ID :%s') % self.order_spacefill_id
                                        )
                else:
                    raise UserError(
                            _('Error from API :'))
        


    def prepare_entry_vals(self,scheduled_date):
        vals = {
            "shipper_order_reference": self.name,
            "warehouse_id": self.picking_type_id.warehouse_id.spacefill_warehouse_account_id,
            "comment": "from odoo",
            "planned_execution_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(scheduled_date)
            },
            "carrier_name": None,
            "carrier_phone_number": None,
            "transport_management_owner": "PROVIDER",
            "entry_expeditor": self.partner_id.name,
            "entry_expeditor_address_line1":self.partner_id.street,
            "entry_expeditor_address_zip": self.partner_id.zip,
            "entry_expeditor_address_details": None,
            "entry_expeditor_address_city": self.partner_id.city,
            "entry_expeditor_address_country": self.partner_id.country_id.name,
            "entry_expeditor_address_lat": None,
            "entry_expeditor_address_lng": None,
            "entry_expeditor_planned_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(scheduled_date)
            },
            "edi_erp_id": self.id,
            "edi_wms_id": None,
            "edi_tms_id": None,
            "transfered_to_erp_at": datetime.utcnow().isoformat() + "Z",
            "transfered_to_wms_at": None,
            "transfered_to_tms_at": None,

        }
        return vals
    def prepare_exit_vals(self,scheduled_date):
        """Prepare the values of the order to export on Spacefill.
        
        :param scheduled_date: Scheduled date of the order"""
        vals= {
            "shipper_order_reference": self.name,
            "warehouse_id": self.picking_type_id.warehouse_id.spacefill_warehouse_account_id,#
            "comment": "exit from odoo",
            "planned_execution_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(scheduled_date),
            },
            "carrier_name":None,
            "carrier_phone_number": None,
            "transport_management_owner": "PROVIDER",
           "exit_final_recipient":self.partner_id.name,
            "exit_final_recipient_address_line1": self.partner_id.street,
            "exit_final_recipient_address_zip": self.partner_id.zip,
            "exit_final_recipient_address_details": None,
            "exit_final_recipient_address_city": self.partner_id.city,
            "exit_final_recipient_address_country": self.partner_id.country_id.name,
            "exit_final_recipient_address_lat": None,
            "exit_final_recipient_address_lng": None,
            "exit_final_recipient_planned_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(scheduled_date),
            },
            "edi_erp_id": self.id,
            "edi_wms_id": None,
            "edi_tms_id": None,
            "transfered_to_erp_at": datetime.utcnow().isoformat() + "Z",
            "transfered_to_wms_at": None,
            "transfered_to_tms_at": None,                        
        }        

        return vals

 
    