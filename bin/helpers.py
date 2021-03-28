#!/usr/bin/env python

# Modules
import logging
import sys
import re
from getpass import getpass
import yaml
import json
import argparse

# User-defined function
def get_creds(input_type):
    """
    This function collects the credentails to connect to the network elements.
    Input: source of collection: 'cli', 'file', or 'api' 
    """
    logging.info('Collecting credentials...')
    result ={}

    if input_type == 'cli':
        print('Please, provide the credentials for the network functions and NetBox token: ')
        result['user'] = str(input('Username > '))
        result['pass'] = getpass('Password > ')
        result['nb_token'] = getpass('NetBox Token > ')

    logging.info('Credentials are collected.')
    return result


def get_data(file_path):
    """
    This function opens the external file in JSON or YAML format and imports the data as dictionary.
    Input: path to the file with the format YAML or JSON.
    """
    if re.match('^.*\.(yaml|yml)$', file_path):
        with open(file_path, 'r') as f:
            temp_dict = yaml.load(f.read(), Loader=yaml.FullLoader)

        return temp_dict

    elif re.match('^.*\.json$', file_path):
        with open(file_path, 'r') as f:
            temp_dict = json.loads(f.read())

        return temp_dict

    else:
        logging.error('The input variables has wrong data type.')
        sys.exit(1)


def get_args():
    # Default ranges
    allowed_operations = {"draw", "analyze"}
    allowed_topology = {"bgp", "lldp", "bfd"}

    parser = argparse.ArgumentParser(prog='OpenConfig Network Topology Grapher', description="This tool is polling the info from devices using gNMI using OpenConfig YANG modules and builds topologies.")
    parser.add_argument('-s', '--save', dest="save", default=False, action='store_true', help="Cache the collected information.")
    parser.add_argument('-l', '--local', dest="local", default=False, action='store_true', help="Use locally stored cache")
    parser.add_argument('-d', '--datacentre', dest="datacentre", default="dc5-lab", help="Choose data centre")
    parser.add_argument('-f', '--failed_nodes', dest="failed_nodes", default=1, type=int, help="Number of failed nodes")
    parser.add_argument('-o', '--operation', dest="operation", default="draw", help=f"Provide operation type. Allowed: {', '.join(allowed_operations)}")
    parser.add_argument('-t', '--topology', dest="topology", default="bgp", help=f"Provide topology type. Allowed: {', '.join(allowed_topology)}")

    result = parser.parse_args()

    # Validating the operation type
    result.operation = set(result.operation.split(","))
    for op in result.operation:
        if op not in allowed_operations:
            logging.error(f"Not supported operation type: {result.operation}")
            sys.exit(f"Not supported operation type: {result.operation}")

    # Valdifating the topology type
    if result.topology not in allowed_topology:
        logging.error(f"Not supported topology type: {result.topology}")
        sys.exit(f"Not supported topology type: {result.topology}")

    return result


def get_inventory(path: str):
    result = {}

    with open(path, "r") as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)

    return result
