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

Stuff you need:
 * A UPS with a USB interface, such as [TrippLite](https://amzn.to/2F5V4aA)
 * A Raspberry Pi or other linux based computer [Pi ZeroW](https://amzn.to/2qsbRdQ)
 * Left Angled 90 Degree Micro USB OTG to Standard B [USB Cable](https://amzn.to/2qpZZcq)
