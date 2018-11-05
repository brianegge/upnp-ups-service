# UPnP UPS service

## Introduction

This code implements a SSDP server and a HTTP server, in order to notify the network that a UPS is available for monitoring. This doesn't support subscription events just yet.

Copy the following into /etc/systemd/system/upnp-ups.service, modify as needed
```
[Unit]
Description=Publish UPS status
After=network.target

[Service]
ExecStart=/home/pi/upnp-ups-service/__main__.py
WorkingDirectory=/home/pi/upnp-ups-service
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```
