#!/bin/sh
# this script requres Mac keychain and a single entry labeled 'Ansible Vault'
# account name is not used

security find-generic-password -gs 'Ansible Vault' 2>&1 | awk -F'"' '/^password/{print $2}'
