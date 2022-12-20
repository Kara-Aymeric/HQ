#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RESTPy is a Python library to interact with all REST API.

:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details


"""

import six
import logging
_logger = logging.getLogger(__name__)

try:
    import requests
    import json
except ImportError:
    pass




class ClientApiMeta(type):
    """
    A Metaclass that automatically injects objects that inherit from API
    as properties.
    """
    def __new__(meta, name, bases, dct):
        abstract = dct.get('__abstract__', False)
        Klass = super(ClientApiMeta, meta).__new__(meta, name, bases, dct)

        if not abstract:
            setattr(
                API,
                property(lambda self: self.get_instance_of(Klass))
            )

        return Klass


@six.add_metaclass(ClientApiMeta)
class API(object):
    """
    Generic API to connect to spacefill
    """
    __abstract__ = True

    def __init__(self, url, token,full_url=False,
                 protocol='rest', verify_ssl=True):
        """
        This is the Base API class which other APIs have to subclass. By
        default the inherited classes also get the properties of this
        class which will allow the use of the API with the `with` statement

        A typical example to extend the API for your subclass is given below::

           from spacefill.api import API

            class Core(API):

                def orders(self):
                    return self.call('', [])

                def get_orders(self):
                    return self.call('', [])


        Example usage ::

            from spacefill.api import API

            with API(url, username, password) as spacefill_api:
                return spacefill_api.call('', [])

        .. note:: Python with statement has to be imported from __future__
        in older versions of python. *from __future__ import with_statement*

        If you want to use the API as a normal class, then you have to manually
        end the session. A typical example is below::

            from spacefill.api import API

            api = API(url, token,)
            api.connect()
            try:
                return api.call('', [])

        :param url: rest spacefill API URL.
        :param token: REST API bearer token
        :param full_url: If set to true, then the `url` is expected to
                    be a complete URL
        :param protocol: rest or rest_json
        :param verify_ssl: for REST API, skip SSL validation if False
        """
        self.url = url
        self.token = token
        self.protocol = protocol
        self.verify_ssl = verify_ssl


    def call(self, type, resource_path, data):
        """
        Proxy for REST call API
        """
        payload = {}
        if data:
            payload = json.dumps(data)
        headers = {
        'Authorization': 'Bearer' + ' ' + self.token,
        }
        response = requests.request(type, resource_path, headers=headers, data=payload, verify=self.verify_ssl)
        if self._check_response(response):
            return response.json()

    
    def create(self, ressource, data):
        """
        Create a new resource.

        :param ressource: The ressource to create
        :param data: The data to create the ressource with
        """ 
        return self.call('POST', ressource, data)

    def update(self, ressource, data):
        """
        Update a resource.

        :param ressource: The ressource to update
        :param data: The data to update the ressource with
        """
        return self.call('PUT', ressource, data)
    
    def search(self, ressource, filters, offset=0, limit=None):
        """
        Search for resources.

        :param ressource: The ressource to search for
        :param filters: The filters to apply to the search

        return ids
        """
        string_filters = ''
        for key, value in filters.items():
            string_filters += str(key) + '=' + str(value) + '&'
        if limit:
            string_filters += 'limit=' + str(limit)
        ressource = ressource + '?' + string_filters
        items = self.call('GET', ressource, {})
        if items.get('total') == 0:
            return False
        ids = []
        for k,v in items.items():
            if isinstance(v, list):
                for val in v:
                    ids.append(val['id'])
        return ids
    
    def search_read(self, ressource, filters, offset=0, limit=None):
        """
        Search for resources.

        :param ressource: The ressource to search for
        :param filters: The filters to apply to the search

        return dict vlaues
        """
        string_filters = ''
        for key, value in filters.items():
            string_filters += str(key) + '=' + str(value) + '&'
        if limit:
            string_filters += 'limit=' + str(limit)
        ressource = ressource + '?' + string_filters
        items = self.call('GET', ressource, {})
        for k,v in items.items():
            if k == 'items':
                return v
    
    def browse(self, ressource, fields=None):
        """
            Return data based on an ID, \
            possibility to specify the fields to return

        Args:
            ressource (str): Full URL with ID
            fields (list): List of field values to return

        Returns:
            dict: dictionary fields,values
        """
        items = self.call('GET', ressource, {})
        if isinstance(fields, list):
            data = {}
            for field in fields:
                data.update({
                    field: items[field]
                })
            return data
        return items

    
    def _check_response(self, response):
        """
        Check the response from the server. If the response is not
        200, then raise an exception.

        :param response: The response from the server
        """
        if response.status_code != 200:
            logging.error('Error %s',response.text)
        else:
            return True


    def get_instance_of(self, Klass):
        """
        Return an instance of the client API with the same auth credentials
        that the API server was instanciated with. The created instance is
        cached, so subsequent requests get an already existing instance.

        :param Klass: The klass for which the instance has to be created.
        """
        with self.lock:
            value = self.__dict__.get(Klass.__name__, self._missing)
            if value is self._missing:
                value = Klass(
                    self.url,
                    self.token,
                    self.version,
                    True,
                    self.protocol,
                )
                self.__dict__[Klass.__name__] = value.__enter__()
            return value
