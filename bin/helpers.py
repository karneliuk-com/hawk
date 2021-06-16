#!/usr/bin/env python
#(c)2021, Karneliuk.com

# Modules
import logging
import sys
import re
from getpass import getpass
import yaml
import json
import argparse
import os


# User-defined function
def get_creds(config: dict = {}):
    """
    This function collects the credentails to connect to the network elements.
    Input: source of collection: 'cli', 'file', 'env', or 'any'. 
    """
    logging.info('Collecting credentials...')

    allowed_cred_types = {"any", "cli", "env", "file"}
    result = {}
    creds_set = False

    config["credentials"]["type"] = config["credentials"]["type"] if config["credentials"]["type"] in allowed_cred_types else "any"

    # Checking environmnt variables
    if config["credentials"]["type"] == "any" or "env":
        try:
            env_vars = os.environ

            result['user'] = env_vars["HAWK_USER"]
            result['pass'] = env_vars["HAWK_PASS"]

            if config["inventory"]["type"] == "netbox":
                result['nb_token'] = env_vars["NB_TOKEN"]
            
            creds_set = True

            logging.info("Credentials picked up from the environment.")

        except KeyError:
            logging.info("Credentials CANNOT be set from environment.")

    # Checking file settings
    if config["credentials"]["type"] == "file" or (config["credentials"]["type"] == "any" and not creds_set):
        try:
            if config["inventory"]["type"] == "netbox":
                result['nb_token'] = config["inventory"]["parameters"]["token"]

            else:
                inv = get_data(config["inventory"]["parameters"]["path"])

                for entry in inv:
                    result["user"] = entry["username"]
                    result["pass"] = entry["password"]

                creds_set = True

            result["user"] = None
            result["pass"] = None

            logging.info("Credentials picked up from the files.")

        except KeyError:
            logging.info("Credentials CANNOT be set from files.")        
    
    # Collecting CLI settings
    if config["credentials"]["type"] == 'cli' or (config["credentials"]["type"] == "any" and not creds_set):
        print('Please, provide the credentials for the network functions and NetBox token: ')
        result['user'] = str(input('Username > '))
        result['pass'] = getpass('Password > ')
        
        result['nb_token'] = getpass('NetBox Token > ') if not 'nb_token' in result else result['nb_token']

    logging.info('Credentials are collected.')
    return result


def get_data(file_path: str):
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
    allowed_operations = {"draw", "analyze", "show-hosts"}
    allowed_topology = {"bgp-ipv4", "bgp-ipv6", "bgp-evpn", "lldp", "bfd"}
    allowed_node_types = {"leaf", "spine", "border", "aggregate"}

    parser = argparse.ArgumentParser(prog='OpenConfig Network Topology Grapher', description="This tool is polling the info from devices using gNMI using OpenConfig YANG modules and builds topologies.")
    parser.add_argument('-s', '--save', dest="save", default=False, action='store_true', help="Cache the collected information.")
    parser.add_argument('-l', '--local', dest="local", default=False, action='store_true', help="Use locally stored cache")
    parser.add_argument('-d', '--datacentre', dest="datacentre", default="nrn", help="Choose data centre")
    parser.add_argument('-f', '--failed_nodes', dest="failed_nodes", default=1, type=int, help="Number of failed nodes")
    parser.add_argument('-ft', '--failed_node_types', dest="failed_node_types", default="spine,aggregate", help=f"Type of the failed nodes to analyse. Allowed: {', '.join(allowed_node_types)}")
    parser.add_argument('-fn', '--failed_node_names', dest="failed_node_names", default="", help="Name of the specific nodes, which shall be failed.")
    parser.add_argument('-ct', '--checked_node_types', dest="checked_node_types", default="leaf,border", help=f"Type of the nodes, which connections shall be checked during simulation. Allowed: {', '.join(allowed_node_types)}")
    parser.add_argument('-cn', '--checked_node_names', dest="checked_node_names", default="", help="Number of specific nodes, which connections shall be checked during simulation.")
    parser.add_argument('-o', '--operation', dest="operation", default="draw", help=f"Provide operation type. Allowed: {', '.join(allowed_operations)}")
    parser.add_argument('-t', '--topology', dest="topology", default="bgp-ipv4", help=f"Provide topology type. Allowed: {', '.join(allowed_topology)}")

    result = parser.parse_args()

    # Validating the operation type
    result.operation = set(result.operation.split(","))
    for op in result.operation:
        if op not in allowed_operations:
            logging.error(f"Not supported operation type: {result.operation}")
            sys.exit(f"Not supported operation type: {result.operation}")

    # Validating the failed node types
    result.failed_node_types = set(result.failed_node_types.split(","))
    for op in result.failed_node_types:
        if op not in allowed_node_types:
            logging.error(f"Not supported node type: {result.failed_node_types}")
            sys.exit(f"Not supported node type: {result.failed_node_types}")

    # Validating the specific failed nodes
    result.failed_node_names = set(result.failed_node_names.split(",")) if result.failed_node_names  else {}

    # Validating the checked node types
    result.checked_node_types = set(result.checked_node_types.split(","))
    for op in result.checked_node_types:
        if op not in allowed_node_types:
            logging.error(f"Not supported node type: {result.checked_node_types}")
            sys.exit(f"Not supported node type: {result.checked_node_types}")

    # Validating the specific checked nodes
    result.checked_node_names = set(result.checked_node_names.split(",")) if result.checked_node_names  else {}

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


def initialization(file_path: str):
    logging.info("Initializing the HAWK...")
    result = {}

    try:
        result = get_data(file_path)
        logging.info(f"Initialization is successful from the configuration file '{file_path}'.")

        if result["inventory"]["type"] == "netbox":
                    env_vars = os.environ

                    if "NB_URL" in env_vars and env_vars["NB_URL"]:
                        result["inventory"]["parameters"]["url"] = env_vars["NB_URL"]

        logging.info(f"The NetBox URL is modifed per environment variables.")

    except FileNotFoundError:
        logging.info("Configuration file is not found, using the default parameters.")

        result = {
            'inventory': {
                'type': 'local', 
                'parameters': {
                    'path': './inventory/inventory.yaml'
                }
            }, 
            'logging': {
                'enabled': True, 
                'parameters': {
                    'path': './log/execution.log'
                }
            }, 
            'output': {
                'type': 'local', 
                'parameters': {
                    'path': './output'
                }
            }, 
            'cache': {
                'enabled': True, 
                'parameters': {
                    'path': './.cache/raw_results.json'
                }
            }, 
            'templates': {
                'parameters': {
                    'path': './templates'
                }
            },
            'credentials': {
                'type': 'any'
            },
            'mapping': {
                'data_centre': {'leaf': ['leaf'], 'spine': ['spine'], 'border': ['border'], 'aggregate': ['aggregate'], 'dci': ['dci-gw']}, 
                'service_provider': None, 
                'enterprise': None
            }
        }
        
        logging.info("Initialization is successful with default variables.")

    return result

def cumulus_neighbor_parser(raw_input: str):
    result = []

    for l in raw_input.splitlines():
        tr = l.split(" ")
        if tr[2] != "eth0":
            result.append({"ip_address": tr[0], "mac": tr[4], "vlan": re.sub(r'vlan(\d+)', r'\1', tr[2])})

    return result