#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generator.py - Generates random numbers and publishes them to a Kafka topic.

This script runs on VM1 and acts as a Kafka producer. It generates a random
integer between 1 and 100 every 2 seconds, prepends the VM's IP address to the
number, and sends the resulting string to the 'numbers' Kafka topic.

Author: Rohit Prajapati (itspraja@gmail.com)
GitHub: itspraja (https://github.com/itspraja)
"""

import time
import random
import socket
from kafka import KafkaProducer
from kafka.errors import KafkaError

# --- Configuration ---
KAFKA_BROKER = '192.168.1.100:9092'  # REPLACE WITH VM RUNNING KAFKA BROKER (IN THIS CASE, VM1-GENERATOR)
TOPIC_NAME = 'numbers'
SLEEP_TIME = 2  # Seconds


def get_ip():
    """Gets the IP address of the current machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def main():
    """Main function to generate and send numbers."""
    vm_ip = get_ip()

    try:
        producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER],
                                 value_serializer=lambda v: str(v).encode('utf-8'),
                                 retries=5)

    except KafkaError as e:
        print(f"Error connecting to Kafka: {e}")
        return

    while True:
        number = random.randint(1, 100)
        message = f"{vm_ip}:{number}"
        try:
            future = producer.send(TOPIC_NAME, message)
            record_metadata = future.get(timeout=10)
            print(f"Sent: {message} (Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset})")
        except KafkaError as e:
            print(f"Error sending message: {e}")

        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
