import os
import subprocess
from .utils import read_config_file
from .commands import clone_vm, destroy_vm, start_vm, shutdown_vm, set_ram, set_lan

inventory_file = "inventory.ini"

def clone_vms(filename, diskPath):
    vms = read_config_file(filename)
    for vm in vms:
        clone_vm(vm['name'], vm['flavour'], diskPath)
        set_ram(vm['name'], vm['ram'])
        set_lan(vm['name'], vm['lan'])
        start_vm(vm['name'])


def destroy_vms(filename):
    vms = read_config_file(filename)
    for vm in vms:
        destroy_vm(vm['name'])


def start_vms(filename):
    vms = read_config_file(filename)
    for vm in vms:
        start_vm(vm['name'])


def stop_vms(filename):
    vms = read_config_file(filename)
    for vm in vms:
        shutdown_vm(vm['name'])

def create_inventory_file():
  if not os.path.exists(inventory_file):
    with open(inventory_file, "w") as inventory:
      inventory.write("# Ansible groups\n")

def remove_inventory_hosts():
    with open(inventory_file, "r") as inventory:
        lines = inventory.readlines()
        lines_to_delete = []

    for line in lines:
      if "# Ansible groups" in line:
        break
      else:
        lines_to_delete.append(line)

    for line in lines_to_delete:
      lines.remove(line)

    with open(inventory_file, "w") as inventory:
        inventory.writelines(lines)

def add_inventory_host(filename):
    vms = read_config_file(filename)
    index = -1

    for vm in vms:
        cmd = ["virsh","domifaddr",vm['name']]
        cmd_return = subprocess.run(cmd,capture_output=True) # Get the "cmd return" object
        stdout_string = cmd_return.stdout.decode("utf-8") # Decode "STDOUT" from "bytes" to "str" 
        ip = stdout_string.split() # Get "STDOUT" as a list (split=spaces)
        ip = ip[9].split("/") # "ip[9]" is the ip address with "cidr mask"
        ip = ip[0] # "ip[0]" is the ip address without "cidr mask"

        line_to_add = f"{vm['name']} ansible_host={ip} ansible_user={vm['user']} ansible_port={vm['port']}\n"

        index += 1
        with open(inventory_file, "r") as inventory:
            lines = inventory.readlines()
            lines.insert(index, line_to_add)

        with open(inventory_file, "w") as inventory:
            inventory.writelines(lines)

def manage_inventory(filename):
  create_inventory_file()
  remove_inventory_hosts()
  add_inventory_host(filename)
