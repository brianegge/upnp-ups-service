#!/usr/bin/python3

from lib.ssdp import SSDPServer
from lib.upnp_http_server import UPNPHTTPServer, get_network_interface_ip_address
import uuid
from time import sleep
import logging
from lib.ups import check_ups, Poller
import sys
from threading import Thread

logger = logging.getLogger()
if sys.stdout.isatty():
    logger.setLevel(logging.DEBUG)


def setup_debugging():
    """
    Load PyCharm's egg and start a remote debug session.
    :return: None
    """
    import sys
    sys.path.append('/root/pycharm-debug-py3k.egg')
    import pydevd
    pydevd.settrace('192.168.4.47', port=5422, stdoutToServer=True, stderrToServer=True, suspend=False)


# setup_debugging()

poller = Poller()
thread = Thread(target = poller.run)
thread.start()

device_uuid = '60874e62-e7fb-4bb6-bfbd-f0625230e791' # uuid.uuid4()
local_ip_address = get_network_interface_ip_address()

ups = check_ups()

http_server = UPNPHTTPServer(8088,
                             friendly_name=ups['ups.model'],
                             manufacturer=ups['ups.mfr'],
                             model_description=ups['ups.model'] + ' ' + ups.get('ups.serial',''),
                             model_name=ups['ups.model'],
                             model_number=ups['ups.productid'],
                             serial_number="UPS1234",
                             uuid=device_uuid,
                             presentation_url="http://{}:8088/".format(local_ip_address))
http_server.start()

ssdp = SSDPServer()
ssdp.register('local',
              'uuid:{}::upnp:rootdevice'.format(device_uuid),
              'urn:schemas-upnp-org:device:UPS:1',
              'http://{}:8088/ups.xml'.format(local_ip_address))
ssdp.run()
