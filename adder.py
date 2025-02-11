#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
adder.py - Subscribes to a Kafka topic and calculates the running sum of received numbers.

This script runs on VM2 and acts as a Kafka consumer. It subscribes to the
'numbers' topic, receives messages (which should be in the format "IP:number"),
extracts the number, and adds it to a running total.  The script prints the
received number, the source IP, and the current total.

Author: Rohit Prajapati (itspraja@gmail.com)
GitHub: itspraja (https://github.com/itspraja)
"""

import time
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# --- Configuration ---
KAFKA_BROKER = '192.168.1.100:9092'  # REPLACE WITH VM RUNNING KAFKA BROKER (IN THIS CASE, VM1-GENERATOR)
TOPIC_NAME = 'numbers'
GROUP_ID = 'my-group'


def main():
    """Main function to consume messages and calculate the sum."""
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=GROUP_ID,
            value_deserializer=lambda v: v.decode('utf-8')
        )
    except KafkaError as e:
        print(f"Error connecting to Kafka: {e}")
        return

    total = 0
    try:
        for message in consumer:
            try:
                data = message.value
                ip, number_str = data.split(':')
                number = int(number_str)
                total += number
                print(f"Received from {ip}: {number}, Current Total: {total}, (Topic: {message.topic}, Partition: {message.partition}, Offset: {message.offset})")
            except ValueError as e:
                print(f"Error parsing message: {message.value} - {e}")
            except Exception as e:
                 print(f"An unexpected error occurred: {e}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        consumer.close()
        print("Consumer closed.")



if __name__ == "__main__":
    main()
