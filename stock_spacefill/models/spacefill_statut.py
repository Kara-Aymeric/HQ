# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from datetime import date, datetime

class SpacefillStatut(models.Model):
    _name = "spacefill.statut"
    _description = "spacefill.statut"

    spacefill_statut = fields.Selection([
                    ('WAREHOUSE_NEEDS_TO_CONFIRM_PLANNED_EXECUTION_DATE_STATE','WAREHOUSE_NEEDS_TO_CONFIRM_PLANNED_EXECUTION_DATE_STATE'),
                    ('SHIPPER_NEEDS_TO_SUGGEST_NEW_PLANNED_EXECUTION_DATE_STATE','SHIPPER_NEEDS_TO_SUGGEST_NEW_PLANNED_EXECUTION_DATE_STATE'),
                    ('ORDER_IS_READY_TO_BE_EXECUTED_STATE','ORDER_IS_READY_TO_BE_EXECUTED_STATE'),
                    ('UNLOADING_STARTED_STATE','UNLOADING_STARTED_STATE'),
                    ('UNLOADING_FINISHED_STATE','UNLOADING_FINISHED_STATE'),
                    ('PREPARATION_STARTED_STATE','PREPARATION_STARTED_STATE'),
                    ('PREPARATION_FINISHED_STATE','PREPARATION_FINISHED_STATE'),
                    ('CANCELED_ORDER_STATE','CANCELED_ORDER_STATE'),
                    ('COMPLETED_ORDER_STATE','COMPLETED_ORDER_STATE'),
                    ('FAILED_ORDER_STATE','FAILED_ORDER_STATE'),
                    ('DRAFT_ORDER_STATE','DRAFT_ORDER_STATE')])

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status',
        index=True, 
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    is_default_done = fields.Boolean(string='Default Done')
    is_default_cancel = fields.Boolean(string='Default Cancel')
    is_default_waiting = fields.Boolean(string='Default Waiting')
    is_default_ready = fields.Boolean(string='Default Ready')
    is_ok_to_update =fields.Boolean(string='Authorize update ?',default=False)