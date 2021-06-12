#!/usr/bin/env python
#(c)2021, Karneliuk.com

# Modules
import asyncio
import json
import logging
import os
import datetime
import re


# Own modules
from bin.helpers import get_creds, get_args, initialization, get_data
from bin.collector import AsnycPoller
from bin.addinfo import Extender
import bin.analyzer as an
import bin.structurer as st


# Variables
path_log = './log/execution.log'


# Body
if __name__ == '__main__':
    # Setting logging
    if not os.path.exists(path_log.split('/')[1]):
        os.mkdir(path_log.split('/')[1])

    logging.basicConfig(filename=path_log, level=logging.INFO, format='%(asctime)s.%(msecs)03d+01:00,%(levelname)s,%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    logging.info('Starting application...')
    t1 = datetime.datetime.now()

    # Collecting args
    args = get_args()
    config = initialization("./config.yaml")

    # Preparing the output path
    ts = str(datetime.datetime.now())
    ts = re.sub("\s+", "_", ts)

    config["output"]["parameters"]["path"] += f"/{ts}"

    if not os.path.exists(config["output"]["parameters"]["path"]):
        os.makedirs(config["output"]["parameters"]["path"])

    # Working with the real devices    
    if not args.local:
        # Collecting input
        credentials = get_creds(config=config)
        orders = get_data(config["commands"]["path"])

        # Inventory
        if config["inventory"]["type"] == "netbox":
            nbo = Extender(config, credentials['nb_token'], full=True)
            inventory = asyncio.run(nbo.getAll(args.datacentre))

        else:
#            inventory = 
            pass

        # Polling devices
        logging.info('Starting polling data from devices...')
        MG = AsnycPoller(inventory, credentials)
        collected_data = asyncio.run(MG.collectInfo(orders, args.topology))

        logging.info(f'Information is collected successfully from {len(collected_data)} devices.')

        # Saving collected output to a file if necessary
        if args.save:
            logging.info(f'Saving the collected data into {config["cache"]["parameters"]["path"]}...')
            if not os.path.exists(config["cache"]["parameters"]["path"].split('/')[1]):
                os.mkdir(config["cache"]["parameters"]["path"].split('/')[1])

            with open(config["cache"]["parameters"]["path"], 'w') as f:
                f.write(json.dumps(collected_data, sort_keys=True, indent=4))

            with open(config["cache"]["parameters"]["path2"], 'w') as f:
                f.write(json.dumps(inventory, sort_keys=True, indent=4))

            logging.info(f'File {config["cache"]["parameters"]["path"]} is saved succesfully.')

    # Working with the local cache
    else:
        collected_data = json.loads(open(config["cache"]["parameters"]["path"], "r").read())
        inventory = json.loads(open(config["cache"]["parameters"]["path2"], "r").read())

        logging.info(f'Vars are succesfully loaded from cache at {config["cache"]["parameters"]["path"]}.')

    # Working with Network Graph
    network_graph, broken_links_list = an.analyze_bgp(collected_data, inventory, config["mapping"], args.datacentre)
    
    # Drawing topology
    if "draw" in args.operation:
        # Drawing BGP
        if re.match("^bgp-.*", args.topology):
            an.draw_bgp(network_graph, config["output"]["parameters"]["path"], args.datacentre)

    # Analyzing failre scenarios
    if "analyze" in args.operation:
        # Analyzing BGP node failures
        if re.match("^bgp-.*", args.topology):
            an.bgp_failure_analysis(network_graph, broken_links_list, config["output"]["parameters"]["path"], config["templates"]["parameters"]["path"], 
                                    args.failed_nodes, args.failed_node_types, args.failed_node_names, args.checked_node_types, args.checked_node_names)

    # Providing details about connected hosts
    if "show-hosts" in args.operation:
        # Building joint table of all connected hosts
        tch = st.provide_connected_hosts(collected_data)
        st.connected_hosts_csv(tch, config["output"]["parameters"]["path"], args.datacentre)

    logging.info(f'The execution is complete successfully in {datetime.datetime.now() - t1}')