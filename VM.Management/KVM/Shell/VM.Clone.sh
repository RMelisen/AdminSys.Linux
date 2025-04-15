#!/bin/bash

CONFIG_FILE="/home/rmeli/Documents/Admin.Sys.Linux.Git/AdminSys.Linux/VM.Management/KVM/Shell/VM.Config.conf"
DISK_DIR="/home/rmeli/Documents/KVM/KVM"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "File [$CONFIG_FILE] doesn't exists"
    exit 1
fi

# Read and process each config file line (IFS command sets the "internal field separator")
while IFS=' ' read -r VM_SOURCE VM_TARGET_PREFIX N_CLONES NETWORK RAM VCPU OSVERSION; do
    # Ignore empty lines and comments
    [[ -z "$VM_SOURCE" || "$VM_SOURCE" =~ ^# ]] && continue

    # Double check for hidden whitespaces
    VM_SOURCE=$(echo "$VM_SOURCE" | tr -d '[:space:]')
    VM_TARGET_PREFIX=$(echo "$VM_TARGET_PREFIX" | tr -d '[:space:]')
    N_CLONES=$(echo "$N_CLONES" | tr -d '[:space:]')
    NETWORK=$(echo "$NETWORK" | tr -d '[:space:]')
    RAM=$(echo "$RAM" | tr -d '[:space:]')
    VCPU=$(echo "$VCPU" | tr -d '[:space:]')
    OSVERSION=$(echo "$OSVERSION" | tr -d '[:space:]')

    echo "Cloning [$VM_SOURCE] to [$VM_TARGET_PREFIX] ($N_CLONES clones)"
    echo "Network : $NETWORK | RAM : ${RAM}MB | vCPU : ${VCPU}"

    # Check if source VM exists
    if ! virsh list --all | grep -qw "$VM_SOURCE"; then
        echo "Error : Virtual machine [$VM_SOURCE] doesn't exists !"
        continue
    fi

    # Create $N_CLONES number of clones
    for ((i=1; i<=N_CLONES; i++)); do
        VM_TARGET="${VM_TARGET_PREFIX}-$i"
        DISK_SOURCE="$DISK_DIR/$VM_SOURCE.qcow2"
        DISK_TARGET="$DISK_DIR/$VM_TARGET.qcow2"

        # Check if disks repository exists
        if [ ! -f "$DISK_SOURCE" ]; then
            echo "Error : Source repository [$DISK_SOURCE] doesn't exists !"
            continue
        fi

        echo "Creating [$VM_TARGET] ..."

        # Copy image disk
        cp "$DISK_SOURCE" "$DISK_TARGET"

        # Create new VM with "virt-install" (no GUI)
        virt-install --name "$VM_TARGET" \
            --ram "$RAM" \
            --vcpus "$VCPU" \
            --disk path="$DISK_TARGET",format=qcow2 \
            --network network="$NETWORK" \
            --os-variant $OSVERSION \
            --graphics none \
            --import \
            --noautoconsole

        # Check if cloning was succesfull
        if [ $? -eq 0 ]; then
            echo "Cloning succesfull : $VM_TARGET created"
        else
            echo "Fail to clone [$VM_SOURCE] to [$VM_TARGET]"
            continue
        fi

        # Start VM
        virsh start "$VM_TARGET"
        echo "[$VM_TARGET] started"

        # Attach network interface after starts
        sleep 5  # Waiting 5 seconds to be sure that the VM is indeed started
        virsh attach-interface --domain "$VM_TARGET" --type network --source "$NETWORK" --config --live

        echo "Network interface [$NETWORK] attached to [$VM_TARGET]"
        echo "-----------------------------------------------------"
    done
done < "$CONFIG_FILE"

