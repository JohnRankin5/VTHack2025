#!/bin/bash

# Enable IP Forwarding (Router Mode)
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Set Up NAT (Network Address Translation)
# Since you don't need WWW access, we won't configure NAT or iptables rules for internet access.

# Set Up DHCP Server with dnsmasq
echo "interface=wlan0" | sudo tee /etc/dnsmasq.conf
echo "dhcp-range=192.168.1.100,192.168.1.200,12h" | sudo tee -a /etc/dnsmasq.conf
sudo systemctl restart dnsmasq

# Set Up Wireless Access Point using hostapd
echo "interface=wlan0" | sudo tee /etc/hostapd/hostapd.conf
echo "driver=nl80211" | sudo tee -a /etc/hostapd/hostapd.conf
echo "ssid=TWK-WIFI" | sudo tee -a /etc/hostapd/hostapd.conf  # Set your Wi-Fi network name to TWK-WIFI
echo "hw_mode=g" | sudo tee -a /etc/hostapd/hostapd.conf
echo "channel=7" | sudo tee -a /etc/hostapd/hostapd.conf  # Set the channel
echo "ieee80211n=1" | sudo tee -a /etc/hostapd/hostapd.conf  # Enable 802.11n (Wi-Fi N)
echo "wpa=2" | sudo tee -a /etc/hostapd/hostapd.conf
echo "wpa_passphrase=TWKTWKTWKTWKTWK" | sudo tee -a /etc/hostapd/hostapd.conf  # Set your Wi-Fi password

# Point hostapd to its config file
echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" | sudo tee /etc/default/hostapd

# Start hostapd to enable Wi-Fi AP
sudo systemctl start hostapd
sudo systemctl enable hostapd

# Enable and Start SSH Server
sudo systemctl enable ssh
sudo systemctl start ssh

# Print Success Message
echo "Router and Wi-Fi AP setup completed. SSH is enabled for remote access."
echo "Connect to the network 'TWK-WIFI' with the password 'TWKTWKTWKTWKTWK'."
