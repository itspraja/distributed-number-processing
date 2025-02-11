# distributed-number-processing
A Distributed Number Processing System with Kafka

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`distributed-number-processing` is a simple demonstration of a distributed number processing system built using Arch Linux, KVM virtual machines, and Kafka.  It consists of two Python scripts:

*   **`generator.py`:**  Running on VM1, this script generates random numbers, tags them with the VM's IP address, and publishes them to a Kafka topic.
*   **`adder.py`:** Running on VM2, this script subscribes to the Kafka topic, receives the numbers, and calculates a running total.

This project showcases the following concepts:

*   Virtual Machine creation and management using KVM and `virt-manager`.
*   Basic Arch Linux setup and configuration.
*   Network configuration for inter-VM communication (bridged networking).
*   Deployment and configuration of Apache Kafka.
*   Use of `kafka-python` to interact with Kafka from Python.
*   Building a simple distributed application.

## Architecture

The system consists of two VMs:

*   **VM1 (Generator):** Runs `generator.py` and (in this example) Kafka.
*   **VM2 (Adder):** Runs `adder.py`.

Communication between the VMs occurs through a Kafka topic named `numbers`.  A bridged network configuration is used for simplicity, allowing the VMs to communicate directly with each other and the host machine.

## Prerequisites

*   An Arch Linux host machine.
*   KVM and related tools installed (`qemu`, `virt-manager`, `libvirt`, etc.).  See the "Setup" section for detailed instructions.
*   A basic understanding of the Arch Linux installation process.
*   Python 3 and `pip` installed on both VMs.
*   An AUR helper (yay or paru) installed on the VM that will run Kafka.

## Setup

1.  **Install KVM and Tools (Host):**

    ```bash
    sudo pacman -S qemu virt-manager virt-viewer dnsmasq vde2 bridge-utils openbsd-netcat
    sudo systemctl enable libvirtd.service
    sudo systemctl start libvirtd.service
    sudo usermod -a -G libvirt $(whoami)  # Log out and back in after this!
    ```

2.  **Create VMs:**

    *   Use `virt-manager` to create two Arch Linux VMs (VM1 and VM2).
    *   Use an Arch Linux ISO image.
    *   Configure bridged networking for both VMs.
    *   Allocate sufficient RAM (2GB+) and disk space (10GB+).

3.  **Install Arch Linux:**
    *   Boot from the ISO.
    *   Partition your disk (creating an EFI System Partition).
    *   Format and mount partitions.
    *   Install the base system: `pacstrap /mnt base linux linux-firmware git'
    *   Generate fstab: `genfstab -U /mnt >> /mnt/etc/fstab`
    *   Chroot: `arch-chroot /mnt`
    *   Clone this repository:
    ```bash
        git clone https://github.com/itspraja/distributed-number-processing.git
        cd distributed-number-processing
        chmod +x install-arch.sh
        ./install-arch.sh <vm_hostname> # Example: ./install-arch.sh vm1-generator
    ```
    *   Exit chroot, unmount, and reboot.
    *   **IMPORTANT:** Change the root and user passwords after the first boot! The default user is `user` with password `password`.

4.  **Install Kafka (on VM1 or VM2):**

    ```bash
    sudo pacman -S kafka
    ```

    *   Configure Kafka:
        *   Edit `/etc/kafka/server.properties`.
        *   Set `listeners` and `advertised.listeners` to the VM's IP address and port 9092 (e.g., `listeners=PLAINTEXT://192.168.1.100:9092`).
        *   Leave `zookeeper.connect` as `localhost:2181` (if using the bundled Zookeeper).

    *   Start Zookeeper and Kafka:

        ```bash
        sudo systemctl enable --now zookeeper kafka
        ```

5.  **Install `kafka-python-ng` (Both VMs):**

    ```bash
    python -m venv kafkaEnv
    source kafkaEnv/bin/activate
    pip install kafka-python-ng
    ```

6. **Clone the repository**
    ```bash
    git clone https://github.com/itspraja/distributed-number-processing.git
    cd distributed-number-processing
    ```

## Running the Application

**Change the Configuration (IP Address) of the Kafka Broker in both Python Files.**

1.  **On VM1 (or the VM running Kafka):**

    ```bash
    python generator.py
    ```

2.  **On VM2:**

    ```bash
    python adder.py
    ```

You should see output from both scripts, demonstrating the number generation and the running total calculation.

## Optional: systemd Services
Create systemd unit files to run the Python scripts as services for automatic startup. Create files named `/etc/systemd/system/generator.service` and `/etc/systemd/system/adder.service`, adjust the `WorkingDirectory`, `ExecStart`, and `User` to reflect your setup.

Example `generator.service` file:

```bash
[Unit]
Description=Number Generator Service
After=network.target

[Service]
WorkingDirectory=/path/to/your/script/directory
ExecStart=/usr/bin/python /path/to/your/script/directory/generator.py
Restart=always
User=yourusername
Group=users
Environment=PATH=/usr/bin:/usr/local/bin
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=number-generator

[Install]
WantedBy=multi-user.target
```

Enable and start services with:
```bash
sudo systemctl enable generator.service # On VM that runs generator.py
sudo systemctl start generator.service
sudo systemctl enable adder.service    # On VM that runs adder.py
sudo systemctl start adder.service
```

License

This project is licensed under the MIT License - see the LICENSE file for details.  
