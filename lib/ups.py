import subprocess
import re

def check_ups():
    # output = subprocess.check_output(["/bin/cat", "test/cyberpower-off.txt"])
    output = subprocess.check_output(["/bin/upsc", "myups"])
    result = {}
    for line in output.splitlines():
        name, value = re.split(': ', line.decode())
        result[name] = value.strip()
    return result
