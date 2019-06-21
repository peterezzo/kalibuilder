#!/usr/bin/env python3
"""
Parallels Dynamic Inventory Plugin for Ansible

Author: Pete Ezzo <peter.ezzo1@verizon.com>
"""

import argparse
import json
import subprocess
import paramiko


def _get_ssh_auth_methods(ip, port):
    t = paramiko.Transport(f'{ip}:{port}')
    try:
        t.connect()
        t.auth_none('')
    except paramiko.BadAuthenticationType as err:
        return err.allowed_types
    except paramiko.SSHException:
        pass

    return ''


def _get_pvm_list():
    r = subprocess.run(['prlctl', 'list', '-jif', '--all'], capture_output=True)
    r.check_returncode()
    return json.loads(r.stdout)


def _get_portforward_list():
    r = subprocess.run(['prlsrvctl', 'net', 'info', 'Shared', '-j'], capture_output=True)
    r.check_returncode()
    try:
        forwards = json.loads(r.stdout)["NAT server"]["TCP rules"]
    except KeyError:
        forwards = []
    return forwards


def list_hosts(searchstring='kali'):
    """
    Return a python dict of all hosts with their variables
    """
    hosts = {}
    for vm in _get_pvm_list():
        if searchstring in vm['Name'] and 'running' in vm['State']:
            host = vm['Name']
            uid = vm['ID']

            hosts[host] = host_vars(host, uid)

    return hosts


def print_inventory():
    """
    Return a json blob in ansible-inventory format of all running parallels hosts with kali in their name
    """
    inventory = {
        '_meta': {'hostvars': {}},
        'all': {'children': ['kali', 'ungrouped'], 'hosts': []},
        'kali': {'children': [], 'hosts': []},
        'ungrouped': {'children': [], 'hosts': []}
        }

    hosts = list_hosts()
    for host, variables in hosts.items():
        inventory['kali']['hosts'].append(host)
        inventory['_meta']['hostvars'][host] = variables

    print(json.dumps(inventory))


def host_vars(host, uid):
    """
    Return a python dict of all variables for a host, verbosely
    """
    variables = {
        'ansible_user': 'vagrant',
        'ansible_become_pass': 'vagrant',
        'ansible_host': host,
        'ansible_ssh_port': 22
        }

    # first check is there a local host port forward to vm port 22
    for nat in _get_portforward_list().values():
        if uid in nat['destination IP/VM id'] and nat['destination port'] == 22:
            variables['ansible_host'] = '127.0.0.1'
            variables['ansible_ssh_port'] = nat['source port']

    # second check if auth is password (base box) or key (repeat) because ansible won't let both work
    if 'password' in _get_ssh_auth_methods(variables['ansible_host'], variables['ansible_ssh_port']):
        variables['ansible_ssh_pass'] = 'vagrant'

    return variables


def print_host_with_vars(searchstring):
    """
    Print a json dict of the variables for the host matching searchstring
    """
    try:
        hostdata = list_hosts(searchstring)[searchstring]
    except KeyError:
        hostdata = {}

    print(json.dumps(hostdata))


if __name__ == "__main__":
    # Inventory scripts must accept the --list and --host <hostname> arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--list', help='List all parallels VMs with "kali" in their name', action='store_true')
    parser.add_argument('--host', help='Return the variables for a specific host')

    args = parser.parse_args()

    if args.host:
        print_host_with_vars(args.host)
    else:
        print_inventory()
