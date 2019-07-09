import subprocess
import re
from time import sleep
import requests
import logging

logger = logging.getLogger()

def check_ups():
    # output = subprocess.check_output(["/bin/cat", "test/cyberpower-off.txt"])
    output = subprocess.check_output(["/bin/upsc", "myups"])
    result = {}
    for line in output.splitlines():
        name, value = re.split(': ', line.decode())
        result[name] = value.strip()
    return result

subscribers = {}
last_poll = {}

class Poller():

    def run(self):
        global subscribers, last_poll
        logger.info("Starting poller")
        while True:
          if len(subscribers) > 0:
              poll = check_ups()
              diff = {}
              for k,v in poll.items():
                  if not k in last_poll:
                      diff[k] = v
                  elif last_poll[k] != v:
                      logger.info("{} {}=>{}".format(k,last_poll[k],v))
                      diff[k] = v
              if len(diff) > 0:
                  doc = "<root>\n"
                  for k,v in diff.items():
                      k = k.replace('.', '_')
                      doc += "<{}>{}</{}>\n".format(k,v,k)
                  doc += "</root>"
                  headers = {'Content-type': 'application/xml'}
                  logger.debug("Publishing event: ")
                  logger.debug(doc)
                  for sid,url in subscribers.items():
                      logger.debug("Updating {} at {}".format(sid, url))
                      r = requests.request('NOTIFY', url = url, headers = headers, data = doc)
                      logger.debug("Hub response: ")
                      logger.debug(r)
              last_poll = poll
          sleep(2)

