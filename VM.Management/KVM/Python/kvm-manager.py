#!/usr/bin/python3
#### Modules #####
import os
import sys
import time
import subprocess
from pathlib import Path
import datetime

##### Variables #####
home_dir = Path.home()
vm_list_file = "vm-list.cfg"
inventory_file = "inventory.ini"
kvm_dir = f"{home_dir}/Documents/KVM"

#### Functions ####
def clone_vm(vm,distro,ram,lan,kvm_dir):
  template = f"0-{distro}"
  cmd_list = [
    ["virt-clone","--original",template,"--name",vm,"--file",f"{kvm_dir}/{vm}.qcow2"],
    ["virsh","setmaxmem",vm,f"{ram}M","--config"],
    ["virsh","setmem",vm,f"{ram}M","--config"],
    ["virsh","detach-interface",vm,"network","--persistent"],
    ["virsh","attach-interface",vm,"network",lan,"--model","virtio","--persistent"]
  ]

  for cmd in cmd_list:
    subprocess.run(cmd)
  start_vm(vm)

def start_vm(vm):
  cmd = ["virsh","start",vm]
  subprocess.run(cmd)

def shutdown_vm(vm):
  cmd = ["virsh","shutdown",vm]
  subprocess.run(cmd)

def undefine_vm(vm):
  cmd = ["virsh", "destroy",vm]
  subprocess.run(cmd)
  time.sleep(5)
  cmd = ["virsh", "undefine","--remove-all-storage",vm]
  subprocess.run(cmd)

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

def add_inventory_host(vm,user,port):
  global index
  index += 1

  cmd = ["virsh","domifaddr",vm]
  cmd_return = subprocess.run(cmd,capture_output=True) # Get the "cmd return" object
  stdout_string = cmd_return.stdout.decode("utf-8") # Decode "STDOUT" from "bytes" to "str" 
  ip = stdout_string.split() # Get "STDOUT" as a list (split=spaces)
  ip = ip[9].split("/") # "ip[9]" is the ip address with "cidr mask"
  ip = ip[0] # "ip[0]" is the ip address without "cidr mask"

  line_to_add = f"{vm} ansible_host={ip} ansible_user={user} ansible_port={port}\n"

  with open(inventory_file, "r") as inventory:
    lines = inventory.readlines()
    lines.insert(index, line_to_add)

  with open(inventory_file, "w") as inventory:
    inventory.writelines(lines)

def trigger_request(request,line,kvm_dir):
  line = line.strip()
  line = line.split("|")

  vm = line[0]
  distro = line[1]
  ram = line[2]
  lan = line[3]
  user = line[4]
  port = line[5]

  match request:
    case 'clone':
      clone_vm(vm,distro,ram,lan,kvm_dir)
    case 'start':
      start_vm(vm)
    case 'shutdown':
      shutdown_vm(vm)
    case 'undefine':
      undefine_vm(vm)
    case 'inventory':
      add_inventory_host(vm,user,port)

##### Main code ####
try:
  request = sys.argv[1]
except:
  print("**** Usage: clone|start|shutdown|undefine|inventory ****")
  sys.exit(22)

if request == "inventory":
  index = -1
  create_inventory_file()
  remove_inventory_hosts()

with open(vm_list_file, "r") as vm_list:
  run_time = 0
  start_time = int(time.time())

  try:
    for line in vm_list:
      if (line == "\n") or (line.startswith('#')):
        continue
      trigger_request(request,line,kvm_dir)
  except:
    print(f"Error while reading the file {vm_list}", end="\n\n")

  stop_time = int(time.time())
  run_time = str(datetime.timedelta(seconds=(stop_time - start_time)))
  print(f"#### Run Time {run_time} ####")
