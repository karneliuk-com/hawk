# HAWK (Highly-efficient Automated Weapon Kit)
This tool is a corner stone of the Highly-efficient Automated Weapon Kit (HAWK). It intnents to collect the output from the devices in the asynchronous mode and perform the necessary validations either in form of the informaton representation in the necessary data format or comparing various data sets.

## Supported data encoding
- YAML
- JSON
- CSV

## Supported platforms
In general, any supporting SSH.

## Requirements
### Python
Created and tested in Python 3.7 - 3.9

### Used libraries
Watch requirements.txt

## Usage
1. Install the modules from `requirements.txt` using `pip`.
2. Modify the `inventory.yaml` file inside the `inventory` directory per your topology.
3. Execute the script as `./main.py`.
4. Open in the `output` directory the relevant generated reports.

## License
[By using this product you accept the license agreement](LICENSE)

## Dev Log
Release `0.2.0`:
- Adding info polling from netbox regarding the management IPs

Release `0.1.0`:
- First release

## Want to automate networks like profi?
