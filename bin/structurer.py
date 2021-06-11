#!/usr/bin/env python

# Modules
import logging
from csv import DictWriter
import re
from pprint import pprint


# User-defined function
def provide_connected_hosts(cd: list, op: str, dcn: str) -> None:
    """
    Building the the table for all connects hosts
    """
    logging.info("Starting building table...")
    
    with open(f'{op}/{dcn}_connected_hosts.csv', 'w') as f:
        header = ["hostname", "interface", "state", "speed", "description", "vlan", "mac_address", "ip_address"]
        to = {}

        writer = DictWriter(f, fieldnames=header)
        writer.writeheader()

        # Getting devices output
        for d in cd:

            # Structuring output line
            for cn in d:
                if "collection" in cn and cn["collection"] == "interfaces": 
                    if "results" in cn and cn["results"]:
                        for k1, v1 in cn["results"].items():
                            # Selecting only data interfaces
                            if re.match(r'swp.*', k1):
                                to.update({"hostname": cn["hostname"]})
                                to.update({"interface": k1})
                                to.update({"state": v1["linkstate"]})
                                to.update({"speed": v1["speed"]})
                                to.update({"description": v1["iface_obj"]["description"]})
                                
                                # Getting MAC and IPs in Bridge
                                for cn2 in d:
                                    if "collection" in cn2 and cn2["collection"] == "macs": 
                                        if "results" in cn2 and cn2["results"]:
                                            for me in cn2["results"]:
                                                if me["dev"] == k1 and "state" not in me:
                                                    to.update({"vlan": me["vlan"]})
                                                    to.update({"mac_address": me["mac"]})

                                                    # Getting IPs
                                                    for cn3 in d:
                                                        if "collection" in cn3 and cn3["collection"] == "neighbors": 
                                                            if "results" in cn3 and cn3["results"]:
                                                                for ie in cn3["results"]:
                                                                    if ie["mac"] == me["mac"]:
                                                                        to.update({"ip_address": ie["ip_address"]})

                                                                        writer.writerow(to)

                               # Getting MAC and IPs from routed interfaces
                                for cn3 in d:
                                    if "collection" in cn3 and cn3["collection"] == "neighbors": 
                                        if "results" in cn3 and cn3["results"]:
                                            for ie in cn3["results"]:

                                                if re.match(r'swp\d+', ie["vlan"]) and ie["vlan"] == k1:
                                                    to.update({"mac_address": ie["mac"]})
                                                    to.update({"vlan": ie["vlan"]})
                                                    to.update({"ip_address": ie["ip_address"]})

                                                    writer.writerow(to)


def provide_connected_hosts2(cd: list, op: str, dcn: str) -> None:
    """
    Building the the table for all connects hosts
    """
    logging.info("Starting building table...")
    result = []


    if True:
#    with open(f'{op}/{dcn}_connected_hosts.csv', 'w') as f:
#        header = ["hostname", "interface", "state", "speed", "description", "vlan", "mac_address", "ip_address"]
        

        # Getting devices output
        for d in cd:
            to = {}

            # Structuring output line
            for cn in d:
                if "hostname" in cn and "hostname" not in to:
                    to.update({"hostname": cn["hostname"]})
                    to.update({"interfaces": {}})

                if "collection" in cn and cn["collection"] == "interfaces": 
                    if "results" in cn and cn["results"]:
                        for k1, v1 in cn["results"].items():
                            # Selecting only data interfaces
                            if re.match(r'swp.*', k1):
                                to["interfaces"].update({k1: {}})
                                to["interfaces"][k1].update({"state": v1["linkstate"]})
                                to["interfaces"][k1].update({"speed": v1["speed"]})
                                to["interfaces"][k1].update({"description": v1["iface_obj"]["description"]})
                                to["interfaces"][k1].update({"connected_endpoints": []})

                                # Getting MAC and IPs in Bridge
                                for cn2 in d:
                                    if "collection" in cn2 and cn2["collection"] == "macs":
                                        if "results" in cn2 and cn2["results"]:
                                            for me in cn2["results"]:
                                                to2 = {}

                                                if me["dev"] == k1 and "state" not in me:
                                                    to2.update({"vlan": me["vlan"]})
                                                    to2.update({"mac_address": me["mac"]})

                                                    # Getting IPs
                                                    for cn3 in d:
                                                        if "collection" in cn3 and cn3["collection"] == "neighbors": 
                                                            if "results" in cn3 and cn3["results"]:
                                                                for ie in cn3["results"]:
                                                                    if ie["mac"] == me["mac"]:
                                                                        to2.update({"ip_address": ie["ip_address"]})
                                                                        to["interfaces"][k1]["connected_endpoints"].append(to2)

                                # Getting MAC and IPs from routed interfaces
                                for cn3 in d:
                                    if "collection" in cn3 and cn3["collection"] == "neighbors": 
                                        if "results" in cn3 and cn3["results"]:
                                            for ie in cn3["results"]:
                                                to2 = {}

                                                if re.match(r'swp\d+', ie["vlan"]) and ie["vlan"] == k1:
                                                    to2.update({"mac_address": ie["mac"]})
                                                    to2.update({"vlan": ie["vlan"]})
                                                    to2.update({"ip_address": ie["ip_address"]})
                                                    to["interfaces"][k1]["connected_endpoints"].append(to2)

            result.append(to)
  
    pprint(result)