#!/usr/bin/env python
#(c)2021, Karneliuk.com

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
    def __init__(self, config: dict, token: str, full: bool = False):
        self.__url = config["inventory"]["parameters"]["url"]
        self.__mapping = config["mapping"]
        self.__token = token
        self.__full = full
        self.__ssh_timeout = config["ssh"]["timeout"]

        self.__ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.__ssl_context.check_hostname = False
        self.__ssl_context.verify_mode = ssl.CERT_NONE


    async def getAll(self, site_slug):
        logging.info('Starting polling info from NetBox...')
        inventory = []
        tasks = []

        # Preparing list of roles for pulling from NetBox
        roles_in_question = []
        for k1, v1 in self.__mapping["data_centre"].items():
            roles_in_question.extend(v1)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.__ssh_timeout)) as self.__client_session:
            for role in roles_in_question:
                tasks.append(asyncio.ensure_future(self.__single_request2(f"{self.__url}/api/dcim/devices/?site={site_slug}&role={role}")))

            results = await asyncio.gather(*tasks)
            
            for e1 in results:
                if "results" in e1:
                    inventory.extend(e1["results"])

            tasks = []

            for dev in inventory:
                if not dev["primary_ip"]:
                    # Pulling the management IP for Cumulus Linux if that is not set for device
                    if dev["platform"] and "slug" in dev["platform"] and dev["platform"]["slug"] == "cumulus-linux":
                        tasks.append(asyncio.ensure_future(self.__single_request2(f"{self.__url}/api/ipam/ip-addresses/?interface=eth0&device_id={dev['id']}")))

            results = await asyncio.gather(*tasks)
            
            for dev in inventory:
                for if_entry in results:
                    if dev["id"] == if_entry["results"][0]["assigned_object"]["device"]["id"]:
                        dev["primary_ip"] = if_entry["results"][0]

        return inventory


    async def __single_request2(self, url):
        async with self.__client_session.get(url, headers={'Authorization': f'Token {self.__token}'}, ssl=self.__ssl_context) as response:
            result = await response.json()

        return result