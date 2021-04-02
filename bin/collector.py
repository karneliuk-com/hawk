#!/usr/bin/env python

# Modules
import asyncio
import asyncssh
import logging
import json

# Classes
class AsnycPoller(object):
    def __init__(self, targets: list, creds: dict):
        self.__targets = targets
        self.__creds = creds


    async def collectInfo(self, commands: dict, clarification: str):
        """
        This function creates a list of tasks launched in the async mode to the network functions.
        Input: inventory(dict) and credentials(dict)
        """
        logging.info(f'Collecting info from {len(self.__targets)} devices over SSH...')
        tasks = []

        # Chossing instructions based on clarification
        cleared_commands = {}

        for inv_entry in self.__targets:
            if (inv_entry["platform"] and "slug" in inv_entry["platform"]) and inv_entry["platform"]["slug"] not in cleared_commands:
                cleared_commands[inv_entry["platform"]["slug"]] = []
                cleared_commands[inv_entry["platform"]["slug"]] = [cv for ck, cv in commands[inv_entry["platform"]["slug"]].items() if ck == clarification]

            if (inv_entry["platform"] and "slug" in inv_entry["platform"]) and inv_entry["platform"]["slug"] in cleared_commands:
                tasks.append(self.__singleShot(inv_entry, cleared_commands[inv_entry["platform"]["slug"]]))

            else:
                logging.warning(f"There is no commands for {inv_entry['name']}.")

        output = await asyncio.gather(*tasks, return_exceptions=True)

        return output


    async def __singleShot(self, host, commands):
        """
        This function runs the connects to the network functions over SSH in sync mode.
        Input: inventory entry(dict) and credentials(dict)
        """
        results = []
        try:
            logging.info(f'Starting polling for {host["primary_ip"]["address"].split("/")[0]}...')
            async with asyncssh.connect(host['primary_ip']['address'].split('/')[0], username=self.__creds['user'], password=self.__creds['pass'],
                                        known_hosts=None) as conn:
                for ce in commands:
                    result = await conn.run(ce, check=True)
                    sr = {}
                    sr.update({'hostname': host['name']})
                    sr.update({'command': ce})
                    sr.update({'results': json.loads(result.stdout)})
                    results.append(sr)

                logging.info(f'Polling from {host["primary_ip"]["address"].split("/")[0]} SUCCEEDED.')
                return results

        except:
            logging.error(f'Polling from {host["primary_ip"]["address"].split("/")[0]} FAILED.')