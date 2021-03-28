#!/usr/bin/env python

# Modules
import logging
import asyncio
import aiohttp
import ssl

# Classes
class Extender(object):
    """
    This class allows to pull the information from the netbox.
    """
    def __init__(self, url, token, full: bool = False):
        self.__url = url
        self.__token = token
        self.__full = full

        self.__ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.__ssl_context.check_hostname = False
        self.__ssl_context.verify_mode = ssl.CERT_NONE


    async def getMgmtIP(self, inventory):
        logging.info('Starting polling info from NetBox...')
        tasks = []

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as client_session:
            for he in inventory:
                tasks.append(asyncio.ensure_future(self.__single_request(client_session, he['hostname'], he['nos'])))

            results = await asyncio.gather(*tasks)

        logging.info('Polling from NetBox is complete.')
        logging.info('Extending the inventory data...')

        for he in inventory:
            for ree in results:
                if he['hostname'] == ree['results'][0]['interface']['device']['name']:
                    he['ip_address'] = ree['results'][0]['address'].split('/')[0]

        logging.info('Inventory is extended.')

        return inventory


    async def __single_request(self, session, hostname, nos):
        if nos == 'cumulus':
            url = f'{self.__url}/api/ipam/ip-addresses/?interface=eth0&device={hostname}'
        elif nos == 'junos':
            url = f'{self.__url}/api/ipam/ip-addresses/?interface=lo0&device={hostname}'

        async with session.get(url, headers={'Authorization': f'Token {self.__token}'}, ssl=self.__ssl_context) as response:
            result = await response.json()

        return result


    async def getAll(self, site_slug):
        logging.info('Starting polling info from NetBox...')
        inventory = []
        tasks = []

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as self.__client_session:
            tasks.append(asyncio.ensure_future(self.__single_request2(f"{self.__url}/api/dcim/devices/?site={site_slug}&device_type_id=33")))
            tasks.append(asyncio.ensure_future(self.__single_request2(f"{self.__url}/api/dcim/devices/?site={site_slug}&device_type_id=34")))

            results = await asyncio.gather(*tasks)
            
            for e1 in results:
                inventory.extend(e1["results"])

            tasks = []

            for dev in inventory:
                tasks.append(asyncio.ensure_future(self.__single_request2(f"{self.__url}/api/ipam/ip-addresses/?interface=eth0&device_id={dev['id']}")))

            results = await asyncio.gather(*tasks)
            
            for dev in inventory:
                del dev["custom_fields"]
                del dev["config_context"]

                for if_entry in results:
                    if dev["id"] == if_entry["results"][0]["assigned_object"]["device"]["id"]:
                        dev["primary_ip"] = if_entry["results"][0]

        return inventory


    async def __single_request2(self, url):
        async with self.__client_session.get(url, headers={'Authorization': f'Token {self.__token}'}, ssl=self.__ssl_context) as response:
            result = await response.json()

        return result