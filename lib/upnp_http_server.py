from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import netifaces as ni
import lib.ups
import logging
from pprint import pprint

PORT_NUMBER = 8080
# Change this based on the the output from /sbin/ifconfig
DEFAULT_ETHERNET = 'wlan0'
logger = logging.getLogger()

def get_network_interface_ip_address(name=DEFAULT_ETHERNET):
    """
    Get the first IP address of a network interface.
    :param interface: The name of the interface.
    :return: The IP address.
    """
    while True:
        if name not in ni.interfaces():
            logger.error('Could not find interface %s.' % (name))
            name = 'eth0'
        if name not in ni.interfaces():
            logger.error('Could not find interface %s.' % (name))
            exit(1)
        interface = ni.ifaddresses(name)
        if (2 not in interface) or (len(interface[2]) == 0):
            logger.warning('Could not find IP of interface %s. Sleeping.' % (interface))
            sleep(60)
            continue
        return interface[2][0]['addr']


class UPNPHTTPServerHandler(BaseHTTPRequestHandler):
    """
    A HTTP handler that serves the UPnP XML files.
    """

    # Handler for the GET requests
    def do_GET(self):

        if self.path == '/ups_wsd.xml':
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(self.get_wsd_xml().encode())
            return
        if self.path == '/ups.xml':
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(self.get_device_xml().encode())
            return
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Not found.")
            return

    def do_SUBSCRIBE(self):
        pprint(self.headers)
        lib.ups.subscribers.append(self.headers['CALLBACK'][1:-1])
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()
        self.wfile.write(self.get_attributes_xml().encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()
        self.wfile.write(self.get_attributes_xml().encode())

    def get_device_xml(self):
        """
        Get the main device descriptor xml file.
        """
        local_ip_address = get_network_interface_ip_address()
        xml = """<root>
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <device>
        <deviceType>urn:schemas-upnp-org:device:UPS:1</deviceType>
        <friendlyName>{friendly_name}</friendlyName>
        <manufacturer>{manufacturer}</manufacturer>
        <modelDescription>{model_description}</modelDescription>
        <modelName>{model_name}</modelName>
        <modelNumber>{model_number}</modelNumber>
        <serialNumber>{serial_number}</serialNumber>
        <UDN>uuid:{uuid}</UDN>
        <serviceList>
            <service>
                <URLBase>http://{ip}:8088</URLBase>
                <serviceType>urn:ups.example.com:service:UPS:1</serviceType>
                <serviceId>urn:ups.example.com:serviceId:UPS</serviceId>
                <controlURL>/ups</controlURL>
                <eventSubURL/>
                <SCPDURL>/ups_wsd.xml</SCPDURL>
            </service>
        </serviceList>
        <presentationURL>{presentation_url}</presentationURL>
    </device>
</root>"""
        return xml.format(friendly_name=self.server.friendly_name,
                          manufacturer=self.server.manufacturer,
                          model_description=self.server.model_description,
                          model_name=self.server.model_name,
                          model_number=self.server.model_number,
                          serial_number=self.server.serial_number,
                          uuid=self.server.uuid,
                          presentation_url=self.server.presentation_url,
                          ip=local_ip_address)

    @staticmethod
    def get_wsd_xml():
        """
        Get the device WSD file.
        """
        return """<scpd xmlns="urn:schemas-upnp-org:service-1-0">
<specVersion>
<major>1</major>
<minor>0</minor>
</specVersion>
</scpd>"""
    @staticmethod
    def get_attributes_xml():
        """
        return the attributes for the ups
        """
        doc = "<root>\n"
        for k,v in lib.ups.check_ups().items():
            k = k.replace('.', '_')
            doc += "<{}>{}</{}>\n".format(k,v,k)
        doc += "</root>"
        return doc


class UPNPHTTPServerBase(HTTPServer):
    """
    A simple HTTP server that knows the information about a UPnP device.
    """
    def __init__(self, server_address, request_handler_class):
        HTTPServer.__init__(self, server_address, request_handler_class)
        self.port = None
        self.friendly_name = None
        self.manufacturer = None
        self.model_description = None
        self.model_name = None
        self.serial_number = None
        self.uuid = None
        self.presentation_url = None


class UPNPHTTPServer(threading.Thread):
    """
    A thread that runs UPNPHTTPServerBase.
    """

    def __init__(self, port, friendly_name, manufacturer, model_description, model_name,
                 model_number, serial_number, uuid, presentation_url):
        threading.Thread.__init__(self, daemon=True)
        self.server = UPNPHTTPServerBase(('', port), UPNPHTTPServerHandler)
        self.server.port = port
        self.server.friendly_name = friendly_name
        self.server.manufacturer = manufacturer
        self.server.model_description = model_description
        self.server.model_name = model_name
        self.server.model_number = model_number
        self.server.serial_number = serial_number
        self.server.uuid = uuid
        self.server.presentation_url = presentation_url

    def run(self):
        self.server.serve_forever()
