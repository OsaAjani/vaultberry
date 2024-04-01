#!/bin/bash

# Check if root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root"
    exit 1
fi

# Install dependencies
apt update -y && apt install -y pip i2c-tools python3-smbus
pip install --break-system-packages -r requirements.txt

# Enable pigpiod daemon on startup
systemctl enable pigpiod

# Enable i2c interface on the pi (yes 0 is for enable, strangely)
raspi-config nonint do_i2c 0

# Enable PWM on the pi if not already done
line="dtoverlay=pwm-2chan"
if ! grep -q "^$line$" /boot/config.txt; then
    # Append the line to the end of the file
    echo "$line" | sudo tee -a /boot/config.txt > /dev/null
fi

# Copy systemd daemon conf and load it
cp -r ./confs/* /
systemctl daemon-reload
systemctl enable vaultberry.service

# Reboot
reboot
