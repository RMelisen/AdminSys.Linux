import os
import subprocess
import configparser
import time

def clone_vm(config_file, disk_dir):
    # Clone VMs based on config file (at the end of this script)
    
    if not os.path.exists(config_file):
        print(f"Error : Config file [{config_file}] doesn't exists")
        return

    config = configparser.ConfigParser(allow_no_value=True)  # Allow empty lines
    config.read(config_file)

    for section in config.sections():
        vm_source = config[section].get('VM_SOURCE')
        vm_target_prefix = config[section].get('VM_TARGET_PREFIX')
        n_clones = int(config[section].get('N_CLONES'))
        network = config[section].get('NETWORK')
        ram = config[section].get('RAM')
        vcpu = config[section].get('VCPU')
        osversion = config[section].get('OSVERSION')

        print(f"Cloning [{vm_source}] to [{vm_target_prefix}] ([{n_clones}] clones)")
        print(f"Network : [{network}] | RAM : {ram}MB | vCPU : {vcpu}")

        # Check if source VM exists
        try:
            subprocess.run(['virsh', 'list', '--all'], capture_output=True, text=True, check=True)
            if vm_source not in subprocess.run(['virsh', 'list', '--all'], capture_output=True, text=True).stdout:
                raise ValueError(f"Virtual machine [{vm_source}] doesn't exists !")
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Error : {e}")
            continue
        
        # Create n_clones VMs
        for i in range(1, n_clones + 1):
            vm_target = f"{vm_target_prefix}-{i}"
            disk_source = os.path.join(disk_dir, f"{vm_source}.qcow2")
            disk_target = os.path.join(disk_dir, f"{vm_target}.qcow2")

            if not os.path.exists(disk_source):
                print(f"Error : Source image disk [{disk_source}] doesn't exists !")
                continue

            print(f"Creating [{vm_target}] ...")

            # Copier l'image disque
            try:
                subprocess.run(['cp', disk_source, disk_target], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error while copying image disk : {e}")
                continue

            # Creating new VM with "virt-install"
            try:
                virt_install_cmd = [
                    'virt-install',
                    '--name', vm_target,
                    '--ram', ram,
                    '--vcpus', vcpu,
                    '--disk', f'path={disk_target},format=qcow2',
                    '--network', f'network={network}',
                    '--os-variant', osversion,
                    '--graphics', 'none',
                    '--import',
                    '--noautoconsole'
                ]
                subprocess.run(virt_install_cmd, check=True)
                print(f"Cloning succesfull : [{vm_target}] created")
            except subprocess.CalledProcessError as e:
                print(f"Error : Cloning failed : {e}")
                continue    

            try:
                # Start VM and attach network interface
                subprocess.run(['virsh', 'start', vm_target], check=True)
                print(f"[{vm_target}] started")

                time.sleep(5)  # Wait 5 seconds to ensure VM is well started
                subprocess.run(['virsh', 'attach-interface', '--domain', vm_target, '--type', 'network', '--source', network, '--config', '--live'], check=True)
                print(f"Network interface [{network}] attached to [{vm_target}]")
                print("-------------------------------------------------------")
            except subprocess.CalledProcessError as e:
                print(f"Error : Failed to attach network interface : {e}")
                continue

if __name__ == "__main__":
    config_file = "/home/rmeli/Documents/Admin.Sys.Linux.Git/AdminSys.Linux/VM.Management/KVM/Python/VM.Config.conf"
    disk_dir = "/home/rmeli/Documents/KVM/KVM"

    clone_vm(config_file, disk_dir)
