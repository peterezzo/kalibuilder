#!/usr/bin/env python3

import argparse
import json
import paramiko
import socket
import subprocess


def get_ssh_auth_methods(ip, port):
    s = socket.socket()
    s.connect((ip, port))
    t = paramiko.Transport(s)
    t.connect()

    try:
        t.auth_none('')
    except paramiko.BadAuthenticationType as err:
        return err.allowed_types


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
        if 'kali' in vm['Name'] and 'running' in vm['State']:
            hosts.append(vm['Name'])

    vagrant_vars = {'ansible_user': 'vagrant', 'ansible_become_pass': 'vagrant'}
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
                    vars = {'ansible_host': '127.0.0.1', 'ansible_ssh_port': nat['source port']}

                    # second check if auth is password (base box) or key (repeat) because ansible won't let both work
                    if 'password' in get_ssh_auth_methods('127.0.0.1', nat['source port']):
                        vars['ansible_ssh_pass'] = 'vagrant'

                    return vars

            # else go direct for the address
            mac = vm['Hardware']['net0']['mac']
            # FIXME: make it work based on IP rather than implicit DNS
            # grep $mac /Library/Preferences/Parallels/parallels_dhcp_leases

    # catchall empty set
    return {}


def print_host_with_vars(searchstring):
    print(json.dumps(host_vars(searchstring)))


if __name__ == "__main__":
    # Inventory scripts must accept the --list and --host <hostname> arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--list', help='List all parallels VMs with "kali" in their name', action='store_true')
    parser.add_argument('--host', help='Return the variables for a specific host')

    args = parser.parse_args()

    if args.host:
        print_host_with_vars(args.host)
    else:
        list_hosts()
