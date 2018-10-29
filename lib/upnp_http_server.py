from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import netifaces as ni
from lib.ups import check_ups

PORT_NUMBER = 8080

def get_network_interface_ip_address(interface='wlan0'):
    """
    Get the first IP address of a network interface.
    :param interface: The name of the interface.
    :return: The IP address.
    """
    while True:
        if interface not in ni.interfaces():
            logger.error('Could not find interface %s.' % (interface,))
            exit(1)
        interface = ni.ifaddresses(interface)
        if (2 not in interface) or (len(interface[2]) == 0):
            logger.warning('Could not find IP of interface %s. Sleeping.' % (interface,))
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
        self.server.subscriptions += self.headers['CALLBACK']
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
        <manufacturerURL>{manufacturer_url}</manufacturerURL>
        <modelDescription>{model_description}</modelDescription>
        <modelName>{model_name}</modelName>
        <modelNumber>{model_number}</modelNumber>
        <modelURL>{model_url}</modelURL>
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
                          manufacturer_url=self.server.manufacturer_url,
                          model_description=self.server.model_description,
                          model_name=self.server.model_name,
                          model_number=self.server.model_number,
                          model_url=self.server.model_url,
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
        for k,v in check_ups().items():
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
        self.manufacturer_url = None
        self.model_description = None
        self.model_name = None
        self.model_url = None
        self.serial_number = None
        self.uuid = None
        self.presentation_url = None
        self.subscriptions = []


class UPNPHTTPServer(threading.Thread):
    """
    A thread that runs UPNPHTTPServerBase.
    """

    def __init__(self, port, friendly_name, manufacturer, manufacturer_url, model_description, model_name,
                 model_number, model_url, serial_number, uuid, presentation_url):
        threading.Thread.__init__(self, daemon=True)
        self.server = UPNPHTTPServerBase(('', port), UPNPHTTPServerHandler)
        self.server.port = port
        self.server.friendly_name = friendly_name
        self.server.manufacturer = manufacturer
        self.server.manufacturer_url = manufacturer_url
        self.server.model_description = model_description
        self.server.model_name = model_name
        self.server.model_number = model_number
        self.server.model_url = model_url
        self.server.serial_number = serial_number
        self.server.uuid = uuid
        self.server.presentation_url = presentation_url

    def run(self):
        self.server.serve_forever()
