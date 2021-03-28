#!/usr/bin/env python

# Version
__version__ = '0.2.0'


# Modules
import asyncio
import json
import logging
import os
import datetime
import re


# Own modules
from bin.helpers import get_creds, get_data, get_args
from bin.collector import AsnycPoller
from bin.structurer import Structurer
from bin.addinfo import Extender
import bin.analyzer as an


# Variables
path_output = './output'
path_log = './log/execution.log'
path_temp = './.cache/raw_results.json'
path_order = './input/order.json'
path_netbox = 'https://netbox.hosting.thg.com'
path_templates = './templates'


# Body
if __name__ == '__main__':
    # Setting logging
    if not os.path.exists(path_log.split('/')[1]):
        os.mkdir(path_log.split('/')[1])

    logging.basicConfig(filename=path_log, level=logging.INFO, format='%(asctime)s.%(msecs)03d+01:00,%(levelname)s,%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    logging.info('Starting application...')

    # Collecting args
    args = get_args()

    # Preparing the output path
    ts = str(datetime.datetime.now())
    ts = re.sub("\s+", "_", ts)

    path_output += f"/{ts}"

    if not os.path.exists(path_output):
        os.makedirs(path_output)

    # Working with the real devices    
    if not args.local:
        # Collecting input
        credentials = get_creds('cli')
        order = get_data(path_order)

        # Inventory
        nbo = Extender(path_netbox, credentials['nb_token'], full=True)
        inventory = asyncio.run(nbo.getAll(args.datacentre))

        # Polling devices
        logging.info('Starting polling data from devices...')
        MG = AsnycPoller(inventory, credentials)
        collected_data = asyncio.run(MG.collectInfo(order, args.topology))

        logging.info(f'Information is collected successfully from {len(collected_data)} devices.')

        # Saving collected output to a file if necessary
        if args.save:
            logging.info(f'Saving the collected data into {path_temp}...')
            if not os.path.exists(path_temp.split('/')[1]):
                os.mkdir(path_temp.split('/')[1])

            with open(path_temp, 'w') as f:
                f.write(json.dumps(collected_data, sort_keys=True, indent=4))

            logging.info(f'File {path_temp} is saved succesfully.')

    # Working with the local cache
    else:
        collected_data = json.loads(open(path_temp, "r").read())

        logging.info(f'Vars are succesfully loaded from cache at {path_temp}.')

    # Working with Network Graph
    network_graph = an.analyze_bgp(collected_data, args.datacentre)

    # Drawing topology
    if "draw" in args.operation:
        # Drawing BGP
        if args.topology == "bgp":
            an.draw_bgp(network_graph, path_output, args.datacentre)

    # Analyzing failre scenarios
    if "analyze" in args.operation:
        # Analyzing BGP node failures
        if args.topology == "bgp":
            an.bgp_failure_analysis(network_graph, path_output, path_templates, args.failed_nodes)

    logging.info('The execution is complete successfully')