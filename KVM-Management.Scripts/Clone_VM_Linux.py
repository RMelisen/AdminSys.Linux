import os
import subprocess
import configparser
import time

def clone_vm(config_file, disk_dir):
    # Clone des VMs Linux en utilisant les informations du fichier de configuration

    if not os.path.exists(config_file):
        print(f"Erreur : Le fichier {config_file} n'existe pas.")
        return

    config = configparser.ConfigParser(allow_no_value=True)  # Permet les lignes vides
    config.read(config_file)

    for section in config.sections():
        vm_source = config[section].get('VM_SOURCE')
        vm_target_prefix = config[section].get('VM_TARGET_PREFIX')
        n_clones = int(config[section].get('N_CLONES'))
        network = config[section].get('NETWORK')
        ram = config[section].get('RAM')
        vcpu = config[section].get('VCPU')
        osversion = config[section].get('OSVERSION')

        print(f"Clonage de {vm_source} avec prefixe {vm_target_prefix} ({n_clones} clones)")
        print(f"Reseau : {network} | RAM : {ram}MB | vCPU : {vcpu}")

        # Vérifier si la VM source existe
        try:
            subprocess.run(['virsh', 'list', '--all'], capture_output=True, text=True, check=True)
            if vm_source not in subprocess.run(['virsh', 'list', '--all'], capture_output=True, text=True).stdout:
                raise ValueError(f"La VM {vm_source} n'existe pas !")
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Erreur : {e}")
            continue

        for i in range(1, n_clones + 1):
            vm_target = f"{vm_target_prefix}-{i}"
            disk_source = os.path.join(disk_dir, f"{vm_source}.qcow2")
            disk_target = os.path.join(disk_dir, f"{vm_target}.qcow2")

            if not os.path.exists(disk_source):
                print(f"Erreur : Le fichier source {disk_source} n'existe pas !")
                continue

            print(f"Creation de {vm_target}...")

            # Copier l'image disque
            try:
                subprocess.run(['cp', disk_source, disk_target], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de la copie du disque : {e}")
                continue

            # Créer la nouvelle VM avec `virt-install`
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
                print(f"Clonage réussi : {vm_target} créé.")

                # Démarrer la VM et attacher l'interface réseau
                subprocess.run(['virsh', 'start', vm_target], check=True)
                print(f"{vm_target} a été démarré avec succès.")

                time.sleep(5)  # Attendre 5 secondes
                subprocess.run(['virsh', 'attach-interface', '--domain', vm_target, '--type', 'network', '--source', network, '--config', '--live'], check=True)
                print(f"➡️  Interface réseau {network} attachée à {vm_target}.")
                print("----------------------------------------")

            except subprocess.CalledProcessError as e:
                print(f"Échec du clonage ou de l'attachement réseau : {e}")
                continue

if __name__ == "__main__":
    config_file = "/home/rmeli/config_VM_Linux.conf"  # Chemin vers le fichier de configuration
    disk_dir = "/home/rmeli/Documents/4 - KVM/KVM"  # Répertoire des disques

    clone_vm(config_file, disk_dir)
