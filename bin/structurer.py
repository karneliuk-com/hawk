#!/usr/bin/env python

# Modules
import logging
from csv import DictWriter
import os

# Classes
class Structurer(object):
    def __init__(self, raw):
        self.__raw = raw

    def whatIsThere(self, tp):
        logging.info('Creating output directory...')
        if not os.path.exists(tp):
            os.mkdir(tp)

        logging.info('Starting parsing the output')
        for de in self.__raw:
            for ce in de:
                # If other commands are to be parsed, that should be added here as new 'elif' clause
                if ce['command'] == 'net show bridge vlan json':
                    logging.info('Parsing the port/VLAN mapping...')
                    with open(f'{tp}/port_vlan_{ce["hostname"]}.csv', 'w') as f:
                        header = ['device', 'port', 'type', 'VLAN']
                        
                        writer = DictWriter(f, fieldnames=header)
                        writer.writeheader()
                        
                        if ce['results']:
                            for iface_name, iface_vars in ce['results'].items():
                                if 'flags' in iface_vars[0] and "Egress Untagged" in iface_vars[0]['flags']:
                                    writer.writerow({'device': ce['hostname'], 'port': iface_name, 'type': 'access', 'VLAN': iface_vars[0]['vlan']})

                        logging.info('Parsing of the port/VLAN mapping is complete.')

                if ce['command'] == 'net show interface json':
                    logging.info('Parsing the interfaces\' data...')
                    with open(f'{tp}/interfaces_{ce["hostname"]}.csv', 'w') as f:
                        header = ['INTERFACE', 'DESCRIPTION', 'MTU', 'MAC', 'IP', 'UNTAGGED_VLAN', 'TAGGED_VLAN','RX_DRP', 'RX_ERR', 'RX_OK', 'RX_OVR', 'TX_DRP', 'TX_ERR', 'TX_OK', 'TX_OVR']

                        writer = DictWriter(f, fieldnames=header)
                        writer.writeheader()

                        if ce['results']:
                            temp_obj = {}

                            for iface_name, iface_vars in ce['results'].items():
                                temp_obj['INTERFACE'] = iface_name
                                temp_obj['DESCRIPTION'] = iface_vars['iface_obj']['description'] if 'iface_obj' in iface_vars and 'description' in iface_vars['iface_obj'] and iface_vars['iface_obj']['description'] else 'N/A'
                                temp_obj['MTU'] = iface_vars['iface_obj']['counters']['MTU'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'MTU' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['MAC'] = iface_vars['iface_obj']['mac'] if 'iface_obj' in iface_vars and 'mac' in iface_vars['iface_obj'] else 'N/A'
                                temp_obj['IP'] = ' '.join([ip for ip in iface_vars['iface_obj']['ip_address']['allentries']]) if 'iface_obj' in iface_vars and 'ip_address' in iface_vars['iface_obj'] and 'allentries' in iface_vars['iface_obj']['ip_address'] and iface_vars['iface_obj']['ip_address']['allentries'] else 'N/A'
                                temp_obj['UNTAGGED_VLAN'] = iface_vars['iface_obj']['native_vlan'] if 'iface_obj' in iface_vars and 'native_vlan' in iface_vars['iface_obj'] and iface_vars['iface_obj']['native_vlan'] else 'N/A'
                                temp_obj['TAGGED_VLAN'] = iface_vars['iface_obj']['vlan_list'] if 'iface_obj' in iface_vars and 'vlan_list' in iface_vars['iface_obj'] and iface_vars['iface_obj']['vlan_list'] else 'N/A'
                                temp_obj['RX_DRP'] = iface_vars['iface_obj']['counters']['RX_DRP'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'RX_DRP' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['RX_ERR'] = iface_vars['iface_obj']['counters']['RX_ERR'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'RX_ERR' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['RX_OK'] = iface_vars['iface_obj']['counters']['RX_OK'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'RX_OK' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['RX_OVR'] = iface_vars['iface_obj']['counters']['RX_OVR'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'RX_OVR' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['TX_DRP'] = iface_vars['iface_obj']['counters']['TX_DRP'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'TX_DRP' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['TX_ERR'] = iface_vars['iface_obj']['counters']['TX_ERR'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'TX_ERR' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['TX_OK'] = iface_vars['iface_obj']['counters']['TX_OK'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'TX_OK' in  iface_vars['iface_obj']['counters'] else 'N/A'
                                temp_obj['TX_OVR'] = iface_vars['iface_obj']['counters']['TX_OVR'] if 'iface_obj' in iface_vars and 'counters' in iface_vars['iface_obj'] and 'TX_OVR' in  iface_vars['iface_obj']['counters'] else 'N/A'


                                writer.writerow(temp_obj)

                        logging.info('Parsing of the interfaces is complete.')