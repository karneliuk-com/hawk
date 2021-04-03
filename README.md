# HAWK (Highly-efficient Automated Weapon Kit)
Our networks (data centers, service providers, enterprises) make foundation for the successful applications' delivery to customers. Therefore, they are critical infrastructure of the modern digital economics. As such, we need to have an extensive set of tools and processes, which would allow us to plan, model, build, optimise and troubleshoot networks.
This is exactly the purpose of the Highly-efficient Automated Weapon Kit (HAWK). HAWK is a collection of tools to help you to build and operate the networks of any types (data centres, service providers and enterprises) at world-class level.

## Available functionality
At the moment HAWK is being developed as a set of Python tools, which at some point may become something much bigger.

| Tool name | File | Description |
| :--- | :---: | :--- |
| Analyzer | [topology_analyzer.py](topology_analyzer.py) | Visualisation of the network topology (LLDP, BFD, BGP, ISIS) and what-if analysis of the node outage |

## Management Interfaces
The tools is constantly developing, so the changes may be frequent. At the current moment, the following interfaces are supported:
- SSH (in asyncrhonous mode)
- GNMI (in synchronous mode)

## Network Operating System
| Name | Inventory identificator | Implementation |
| :--- | :--- | :--- |
| Cumulus Linux | `cumulus-linux` | Done |
| Arista EOS | `arista-eos` | In progress |
| Nokia SRLinux | `nokia-srlinux` | Planned |

## Credentials
You can use one of 3 approaches:
- Provide variables in environment (`HAWK_USER` for username at network functions, `HAWK_PASS` for password for network functions, `NB_TOKEN` for NetBox access).
- Provide credentials for NetBox in `config.yaml` and username/password in local inventory file.
- Provide all the credentials via cli.

## Requirements
### Python
Created and tested in Python 3.7 - 3.9

### Used libraries
Watch [requirements.txt](requirements.txt)

## Usage
1. Modify the the configuration file: `config.yaml`. If you chose local inventory, modify the `inventory.yaml` file inside the `inventory` directory per your topology.
2. Install the modules from `requirements.txt` using `pip`.
3. Execute the correspondin HAWK tool per the table above (e.g., `python topology_analyzer.py`) .
4. Open in the `output` directory the relevant generated reports.

## License
[By using this product you accept the license agreement](LICENSE)

## Dev Log
Release `0.3.0`:
- First public release.

Release `0.2.1`:
- A lot of rework to generalise the tool.

Release `0.2.1`:
- Changed name of the `main.py`.

Release `0.2.0`:
- Adding info polling from netbox regarding the management IPs

Release `0.1.0`:
- First release

## Want to automate networks like profi?

(c) 2021, Karneliuk.com