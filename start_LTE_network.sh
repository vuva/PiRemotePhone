#!/bin/bash

# Start LTE network interface
sudo ip link set wwan0 down
sudo ip link set wwan0 up
sudo mbim-network /dev/cdc-wdm0 stop
sudo mbim-network /dev/cdc-wdm0 start
# Set IP address
sudo ./mbim-set-ip.sh /dev/cdc-wdm0 wwan0

# Test
ping -4 -c 5 -I wwan0 8.8.8.8 
ping -4 -c 5 -I wwan0 google.com 
ping -6 -c 5 -I wwan0 google.com 
