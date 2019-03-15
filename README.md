# kalibuilder

Ansible scripts to provision a Kali virtual machine for quick use.

## Requirements
1. Parallels Desktop 14 for Mac Business Edition
2. Python3 with ansible installed
3. A Parallels VM with ssh installed and "kalivm" in the name
4. A VM user vagrant/vagrant with passwordless sudo access
5. An ed25519 ssh key on your host machine, with pub key at ~/.ssh/id_ed25519.pub
6. Direct internet access via Parallels shared networking

## Quickstart
1. Create and start a kali VM of any version per the requirements above
2. ./site.yml

## Base box Quickstart
1. Install a kali-light image per the requirements above, named "kali-light-2019.1a"
2. ./rebuild-htb.sh
3. Do any destructive/random stuff in kalivm-htb
4. ./rebuild-htb.sh
