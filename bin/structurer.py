#!/usr/bin/env python

# Modules
import logging
from csv import DictWriter
import re
from copy import deepcopy


# User-defined function
def provide_connected_hosts(cd: list) -> dict:
    """
    Building the the table for all connects hosts
    """
    logging.info("Starting building connected hosts list...")
    result = {}

    # Getting devices output
    for d in cd:
        to = {}

        # Structuring output line
        for cn in d:
            if "hostname" in cn and cn["hostname"] not in result and cn["collection"] == "interfaces":
                to.update({"interfaces": {}})

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

                                                                    tto2 = deepcopy(to2)
                                                                    to["interfaces"][k1]["connected_endpoints"].append(tto2)


                            # Getting MAC and IPs from routed interfaces
                            for cn3 in d:
                                if "collection" in cn3 and cn3["collection"] == "neighbors": 
                                    if "results" in cn3 and cn3["results"]:
                                        for ie in cn3["results"]:
                                            to2 = {}

                                            if re.match(r'swp\d+', ie["vlan"]) and ie["vlan"] == k1:
                                                to2.update({"mac_address": ie["mac"]})
                                                to2.update({"vlan": None})
                                                to2.update({"ip_address": ie["ip_address"]})

                                                to["interfaces"][k1]["connected_endpoints"].append(to2)

                result.update({cn["hostname"]: to})

    return result


def connected_hosts_csv(raw: dict, op: str, dcn: str) -> None:
    """
    This method converts the Python dictionary with nodes to csv
    """
    logging.info("Starting building table...")
    to = {}

    with open(f'{op}/{dcn}_connected_hosts.csv', 'w') as f:
        header = ["hostname", "interface", "state", "speed", "description", "vlan", "mac_address", "ip_address"]

        writer = DictWriter(f, fieldnames=header)
        writer.writeheader()
        
        for k1, v1 in raw.items():
            to.update({"hostname": k1})

            for k2, v2 in v1["interfaces"].items():
                to.update({"interface": k2})
                to.update({"state": v2["state"]})
                to.update({"speed": v2["speed"]})
                to.update({"description": v2["description"]})

                if v2["connected_endpoints"]:
                    for v3 in v2["connected_endpoints"]:
                        to.update({"vlan": v3["vlan"]})
                        to.update({"mac_address": v3["mac_address"]})
                        to.update({"ip_address": v3["ip_address"]})

                        writer.writerow(to)


