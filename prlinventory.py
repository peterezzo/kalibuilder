#!/usr/bin/env python3

import argparse
import json
import subprocess


def get_pvm_list():
    r = subprocess.run(['prlctl', 'list', '-jif', '--all'], capture_output=True)
    r.check_returncode()
    return json.loads(r.stdout)


def get_portforward_list():
    r = subprocess.run(['prlsrvctl', 'net', 'info', 'Shared', '-j'], capture_output=True)
    r.check_returncode()
    try:
        forwards = json.loads(r.stdout)["NAT server"]["TCP rules"]
    except KeyError:
        forwards = []
    return forwards


def list_hosts():
    hosts = []
    for vm in get_pvm_list():
        if 'kalivm' in vm['Name'] and 'running' in vm['State']:
            hosts.append(vm['Name'])
    
    vagrant_vars = {'ansible_user': 'vagrant', 'ansible_ssh_pass': 'vagrant', 'ansible_become_pass': 'vagrant'}
    inventory = {'kali': {'hosts': hosts, 'vars': vagrant_vars}}

    if len(hosts) > 0:
        print(json.dumps(inventory))
    else:
        print(json.dumps({}))


def host_vars(searchstring):
    for vm in get_pvm_list():
        if vm['Name'] == searchstring and 'running' in vm['State']:
            uid = vm['ID']

            # first check for a portforward
            for nat in get_portforward_list().values():
                if uid in nat['destination IP/VM id'] and nat['destination port'] == 22:
                    return {'ansible_host': '127.0.0.1', 'ansible_port': nat['source port']}
            
            # else go direct for the address
            mac = vm['Hardware']['net0']['mac']
            # FIXME: make it work based on IP rather than implicit DNS
    
    # catchall empty set
    return {}


def print_host_with_vars(searchstring):
    print(json.dumps(host_vars(searchstring)))


if __name__ == "__main__":
    # Inventory scripts must accept the --list and --host <hostname> arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--list', help='List all parallels VMs with "kalivm" in their name', action='store_true')
    parser.add_argument('--host', help='Return the variables for a specific host')

    args = parser.parse_args()

    if args.host:
        print_host_with_vars(args.host)
    else:
        list_hosts()
