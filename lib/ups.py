import subprocess
import re
from time import sleep
import requests
from pprint import pprint

def check_ups():
    # output = subprocess.check_output(["/bin/cat", "test/cyberpower-off.txt"])
    output = subprocess.check_output(["/bin/upsc", "myups"])
    result = {}
    for line in output.splitlines():
        name, value = re.split(': ', line.decode())
        result[name] = value.strip()
    return result

subscribers = []
last_poll = {}

class Poller():

    def run(self):
        global subscribers, last_poll
        print("Starting poller")
        while True:
          if len(subscribers) > 0:
              poll = check_ups()
              diff = {}
              for k,v in poll.items():
                  if not k in last_poll or last_poll[k] != v:
                      diff[k] = v
              if len(diff) > 0:
                  doc = "<root>\n"
                  for k,v in diff.items():
                      k = k.replace('.', '_')
                      doc += "<{}>{}</{}>\n".format(k,v,k)
                  doc += "</root>"
                  headers = {'Content-type': 'application/xml'}
                  print("Publishing event: ")
                  pprint(doc)
                  for s in subscribers:
                      print("Updating {}".format(s))
                      r = requests.post(url = s, headers = headers, data = doc) 
                      print("Hub response: ")
                      pprint(r)
              last_poll = poll
          sleep(2)

