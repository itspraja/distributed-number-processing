#!/bin/bash

# Exit on any error
set -e

# Check if the script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Check if a hostname is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <hostname>"
    exit 1
fi
HOSTNAME=$1

# --- Time and Localization ---
ln -sf /usr/share/zoneinfo/UTC /etc/localtime  # UTC is generally best practice for servers
hwclock --systohc

sed -i 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

# --- Hostname ---
echo "$HOSTNAME" > /etc/hostname
cat >> /etc/hosts <<EOF
127.0.0.1   localhost
::1         localhost
127.0.1.1   $HOSTNAME.localdomain $HOSTNAME
EOF


# --- Root Password ---
echo "Setting root password"
echo "root:toor" | chpasswd

# --- Install Packages ---
echo "Installing Packages"
pacman -S --needed --noconfirm grub efibootmgr networkmanager openssh python python-pip nano jdk-openjdk bridge-utils dnsmasq base-devel vim

# --- GRUB Bootloader ---
echo "Configuring GRUB"
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg

# --- Enable Services ---
echo "Enabling Services"
systemctl enable NetworkManager.service
systemctl enable sshd.service

# --- Create User ---
USERNAME=user
PASSWORD=password
echo "Creating user '$USERNAME'..."
useradd -m -G wheel "$USERNAME"
echo "$USERNAME:$PASSWORD" | chpasswd
sed -i 's/# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

echo "Arch Linux Base Install Complete."
echo "Exit chroot, Unmount partitions, and Reboot."
