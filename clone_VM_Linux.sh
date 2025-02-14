#!/bin/bash

CONFIG_FILE="/home/rmeli/config_VM-Linux.conf"
DISK_DIR="/home/rmeli/Documents/4 - KVM/KVM"

# Verifier si le fichier de configuration existe
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Le fichier $CONFIG_FILE n'existe pas."
    exit 1
fi

# Lire et traiter chaque ligne du fichier de configuration
while IFS=' ' read -r VM_SOURCE VM_TARGET_PREFIX N_CLONES NETWORK RAM VCPU; do
    # Ignorer les lignes vides ou celles qui commencent par #
    [[ -z "$VM_SOURCE" || "$VM_SOURCE" =~ ^# ]] && continue

    # Nettoyer les variables pour eviter les espaces caches
    VM_SOURCE=$(echo "$VM_SOURCE" | tr -d '[:space:]')
    VM_TARGET_PREFIX=$(echo "$VM_TARGET_PREFIX" | tr -d '[:space:]')
    N_CLONES=$(echo "$N_CLONES" | tr -d '[:space:]')
    NETWORK=$(echo "$NETWORK" | tr -d '[:space:]')
    RAM=$(echo "$RAM" | tr -d '[:space:]')
    VCPU=$(echo "$VCPU" | tr -d '[:space:]')

    echo "Clonage de $VM_SOURCE avec prefixe $VM_TARGET_PREFIX ($N_CLONES clones)"
    echo "Reseau : $NETWORK | RAM : ${RAM}MB | vCPU : ${VCPU}"

    # Verifier si la VM source existe
    if ! virsh list --all | grep -qw "$VM_SOURCE"; then
        echo "Erreur : La VM $VM_SOURCE n'existe pas !"
        continue
    fi

    # Boucle pour creer le nombre de clones demandes
    for ((i=1; i<=N_CLONES; i++)); do
        VM_TARGET="${VM_TARGET_PREFIX}-$i"
        DISK_SOURCE="$DISK_DIR/$VM_SOURCE.qcow2"
        DISK_TARGET="$DISK_DIR/$VM_TARGET.qcow2"

        # Verifier que le disque source existe
        if [ ! -f "$DISK_SOURCE" ]; then
            echo "Erreur : Le fichier source $DISK_SOURCE n'existe pas !"
            continue
        fi

        echo "Creation de $VM_TARGET..."

        # Copier l'image disque
        cp "$DISK_SOURCE" "$DISK_TARGET"

        # Creer la nouvelle VM avec `virt-install` (desactivation de la console graphique)
        virt-install --name "$VM_TARGET" \
            --ram "$RAM" \
            --vcpus "$VCPU" \
            --disk path="$DISK_TARGET",format=qcow2 \
            --network network="$NETWORK" \
            --os-variant ubuntu22.04 \
            --graphics none \
            --import \
            --noautoconsole  # Empeche l'affichage de la console graphique

        # Verifier si le clonage a reussi
        if [ $? -eq 0 ]; then
            echo "Clonage reussi : $VM_TARGET cree."
        else
            echo "echec du clonage de $VM_SOURCE vers $VM_TARGET."
            continue
        fi

        # Demarrer la VM
        virsh start "$VM_TARGET"
        echo "$VM_TARGET a ete demarre avec succes."

        # Attacher l'interface reseau apres le demarrage
        sleep 5  # Attendre 5 secondes pour s'assurer que la VM est bien lancee
        virsh attach-interface --domain "$VM_TARGET" --type network --source "$NETWORK" --config --live

        echo "➡️  Interface reseau $NETWORK attachee a $VM_TARGET."
        echo "----------------------------------------"
    done
done < "$CONFIG_FILE"

