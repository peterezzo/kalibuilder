#!/bin/sh
# This file expects to run on a Mac with Parallels Desktop 14 for Mac Business Edition
# It does the following activities
#   Deletes existing VM
#   Creates new linked clone of a base VM image
#   Starts the VM
#   Creates a VPN-compatible SSH port forward
#   Retrieves ssh key for the new VM and replaces any old one
#   Calls Ansible to Bootup

BASEVM=kali-light-2019.1a
NEWVM=kalivm-htb
NATPORT=56022
SLEEP=20

# remove old VM if there (forced, ignore errors)
prlctl stop ${NEWVM} 2>/dev/null
prlctl delete ${NEWVM} 2>/dev/null

# build new VM
prlctl clone ${BASEVM} --name ${NEWVM} --linked && \
  prlctl start ${NEWVM} && \
  prlsrvctl net set Shared --nat-tcp-add ${NEWVM},${NATPORT},${NEWVM},22 && \
  echo Waiting ${SLEEP} seconds to boot && \
  sleep ${SLEEP} && \
  echo Fixing up ssh keys && \
  sed -i .old "/127\.0\.0\.1..${NATPORT}/d"  ~/.ssh/known_hosts && \
  ssh-keyscan -p ${NATPORT} -t ed25519 127.0.0.1 >> ~/.ssh/known_hosts && \
  ./site.yml
