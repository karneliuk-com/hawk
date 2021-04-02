#!/usr/bin/env python

# Modules
import networkx
from pyvis.network import Network
import re
import os
from copy import deepcopy
import datetime
from colorama import Fore, Back, Style
import jinja2


# User-defiend function
def get_plane(hn: str):
    hn = int(re.sub("^\D+(\d+)$", "\g<1>", hn.split("-")[0]))
    
    while hn > 4:
        hn -= 4

    return hn


def analyze_bgp(cd: dict, inv: dict, mapping: dict, site: str):
    """
    Bulding the Network Graph out of the BGP outputs
    """
    G = networkx.Graph(name=f"BGP topology for {site}", label=f"BGP topology for {site}", site=site)

    # Building network graph
    for dev in cd:
        bgp_poll = dev[0]

        # Putting device roles based on hostname
        for de in inv:
            if bgp_poll["hostname"] == de["name"]:
                if de["device_role"]["slug"] in mapping["data_centre"]["leaf"]:
                    level = 1
                    plane = None
                    role = "leaf"   
                elif de["device_role"]["slug"] in mapping["data_centre"]["spine"]:
                    level = 3
                    plane = get_plane(bgp_poll["hostname"])
                    role = "spine"
                elif de["device_role"]["slug"] in mapping["data_centre"]["border"]:
                    level = 5
                    plane = None
                    role = "border"
                elif de["device_role"]["slug"] in mapping["data_centre"]["border"]:
                    level = 4
                    plane = None
                    role = "aggregate"

        # Adding nodes to graph
        if "as" in bgp_poll["results"]:
            G.add_node(bgp_poll["hostname"], label=bgp_poll["hostname"], bgp_asn=bgp_poll["results"]["as"], 
                       title=f"{bgp_poll['hostname']}<br>ASN: {bgp_poll['results']['as']}<br>Plane: {plane}<br>Role: {role}", 
                       level=level, plane = plane, role=role)

    # Continuing building network graph 
    for dev in cd:
        if dev[0]["hostname"] in G.nodes:
            if re.match("^CNS.*", dev[0]["hostname"]) or re.match("^PBS.*", dev[0]["hostname"]) or re.match("^PVS.*", dev[0]["hostname"]):
                for peer_if, peer_detail in dev[0]["results"]["peers"].items():
                    if G.nodes[dev[0]["hostname"]]["plane"] == 1:
                        color = "blue"
                    elif G.nodes[dev[0]["hostname"]]["plane"] == 2:
                        color = "green"
                    elif G.nodes[dev[0]["hostname"]]["plane"] == 3:
                        color = "purple"
                    elif G.nodes[dev[0]["hostname"]]["plane"] == 4:
                        color = "brown"

                    # Adding edges to graph
                    if "hostname" in peer_detail:
                        if peer_detail["state"] != "Established":
                            color= "red"

                        if dev[0]["hostname"] in G.nodes and peer_detail["hostname"] in G.nodes:
                            G.add_edge(dev[0]["hostname"], peer_detail["hostname"], label=peer_detail["state"], color=color)

    return G


def draw_bgp(G, po: str, site: str):
    """
    Visualising the BGP topology
    """
    nt = Network(height="600px", width="1200px", heading=G.graph["label"], layout=True)
    nt.from_nx(G)
    nt.toggle_physics(False)

    nt.show(f"{po}/bgp_topology_{site}.html")


def bgp_failure_analysis(G, po: str, pd: str, failed_nodes: int = 1):
    """
    High-function to trigger the node analyses from the BGP perspective
    """
    # Setting nodes to check
    transit_nodes = {"spine", "super-spine"}
    G1 = deepcopy(G)

    # Printing the summary information
    tl = os.get_terminal_size()
    print(Style.RESET_ALL)
    print("=" * tl[0])
    print("Running the failure analysis for:    " + Fore.CYAN + G.graph["site"] + Fore.RESET)
    print("Amount of failed nodes up to:        " + Fore.RED + str(failed_nodes) + Fore.RESET + "\n" + "-" * tl[0])

    # Running analysis
    t1 = datetime.datetime.now()
    connectivity_results = _node_failure_analysis(G1, levels=failed_nodes, failing_nodes=transit_nodes)
    t2 = datetime.datetime.now()

    # Printing results
    print("Results:" + "\n" + "-" * tl[0])
    
    for result_entry in connectivity_results:
        failed_nodes_string = ', '.join(result_entry['failed_nodes']) if result_entry['failed_nodes'] else 'NONE'
        print(f"Failed nodes:                        {failed_nodes_string}")

        if result_entry["connectivity_check"]:
            print(f"Connectivity check:                  " + Fore.GREEN + "PASS" + Fore.RESET + "\n" + "-" * tl[0])
        else:
            print(f"Connectivity check:                  " + Fore.RED + "FAIL" + Fore.RESET + "\n" + "-" * tl[0])

    print("Elapsed time:                        " + Fore.CYAN + f"{t2 - t1}" + Fore.RESET + "\n" + "-" * tl[0])
    print("=" * tl[0])
    print(Style.RESET_ALL)

    # Generating detailed reports
    with open(f"{pd}/bgp_nodes_failure.j2", "r") as f:
        template = jinja2.Template(f.read())

    with open(f"{po}/bgp_nodes_failues_{G.graph['site']}.html", "w") as f:
        f.write(template.render(site=G.graph['site'], elapsed_time=f"{t2 - t1}", results=connectivity_results, failed_nodes=failed_nodes))


def _node_failure_analysis(G, levels: int = 1, failing_nodes: set = {"spine", "super-spine"}, checked_node: str = "", upper_checked_nodes: list = []):
    """
    Recursive function to analyse the impact of outage on the connectivity between the edges
    """
    checked_nodes = deepcopy(upper_checked_nodes)
    results = []

    # Analyzing topology with broken nodes
    if levels != 0:
        levels -= 1

        for n1 in G.nodes.data():
            if n1[1]["role"] in failing_nodes and n1[0] not in checked_nodes and n1[0] != checked_node:
                # Creating temp data structures
                checked_nodes.append(n1[0])
                edge_params = []

                # Saving list of connected edges
                tested_node_adj = list(G.adj[n1[0]])

                # Isolating node from the Graph
                for lost_neighbor in tested_node_adj:
                    edge_params.append(G[n1[0]][lost_neighbor])
                    G.remove_edge(n1[0], lost_neighbor)
                
                # Running conectivity checks
                test_results = _connectivity_check(G)
                result = [{"failed_nodes": [n1[0]], "connectivity_check": False, "broken_paths": test_results["not-ok"]} if test_results["not-ok"] else {"failed_nodes": [n1[0]], "connectivity_check": True}]

                # Running nested check (recursion)
                if levels:
                    nested_results = _node_failure_analysis(G, levels, failing_nodes, n1[0], checked_nodes)

                    upper_result = result[0]

                    for entry in nested_results:
                        entry["failed_nodes"].extend(upper_result["failed_nodes"])
                        result.append(entry)

                # Restoring connectivity
                for ei, lost_neighbor in enumerate(tested_node_adj):
                    G.add_edge(n1[0], lost_neighbor, **edge_params[ei])

                # Modifying results
                results.extend(result)

    # Analyzing the exiting topology
    else:
        # Running conectivity checks
        test_results = _connectivity_check(G)
        result = [{"failed_nodes": [], "connectivity_check": False, "broken_paths": test_results["not-ok"]} if test_results["not-ok"] else {"failed_nodes": [], "connectivity_check": True}] 
        results.extend(result)

    return results


def _connectivity_check(G):
    """
    Functions performing the connectivity check between edge nodes within the graph
    """
    connectivity_matrix = {"ok": [], "not-ok": []}
    # Picking up first edge node
    for n1 in G.nodes.data():
        if n1[1]["role"] == "leaf":

            # Picking up second node
            for n2 in G.nodes.data():
                # Clearing path
                spf_check = None


                if n2[1]["role"] in {"leaf", "exit"} and n1[0] != n2[0] and (n2[0], n1[0]) not in connectivity_matrix["not-ok"]:
                    try:
                        spf_check = networkx.shortest_path(G, source=n1[0], target=n2[0])

                    except networkx.exception.NetworkXNoPath:
                        spf_check = None
                    
                    # Checking path exists
                    connectivity_matrix["ok"].append((n1[0], n2[0])) if spf_check else connectivity_matrix["not-ok"].append((n1[0], n2[0]))

    return connectivity_matrix