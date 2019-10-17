# Windows message host middle man. 
# Use pyinstaller to create a single-file executable from this file.
# Then place it in installation root directory (usually C:\Program Files\Persepolis Download Manager\)

import os
import sys
import struct
from subprocess import (
    Popen,
    PIPE,
    DETACHED_PROCESS,
    CREATE_NEW_PROCESS_GROUP,
    CREATE_BREAKAWAY_FROM_JOB
)


# windows flags to create a detached and independent child process that lives after its parent dies.
creationflags = CREATE_BREAKAWAY_FROM_JOB | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

cwd = sys.argv[0]
current_directory = os.path.dirname(cwd)
persepolis_path = os.path.join(current_directory, "Persepolis Download Manager.exe")

## TODO: fix this temporary solution
## I can not understand the way redirection works in windows.
## Both firefox and Chrome messages from stdin will be parsed successfully in this file.
## But if you skip parsing and redirect them to pdm by Popen(...,stdin=None,...):
## - message from firefox will be redirected to persepolis with no problem.
## - message from Chrome will be dropped.
## As a temporary solution, message is parsed here and saved to a binary file.
## Then file is passed to pdm.
home_address = str(os.path.expanduser("~"))
nhm_request = os.path.join(
    home_address, r'AppData\Local\persepolis_download_manager\nhm_request.bin')
raw_size = sys.stdin.buffer.read(4)  
length = struct.unpack('@I', raw_size)[0]
raw_data = sys.stdin.buffer.read(length)
with open(nhm_request, "w+b") as msg:
    received_message = struct.pack("=I{}s".format(length), length, raw_data)
    msg.write(received_message)

# pass '--nhm' to ensure there will be an unknown arg in parse_args output
# to trigger parsing NHM messages
command = [os.path.abspath(persepolis_path), "--nhm"]
proc = Popen(command, stdin=open(nhm_request, 'r+b'), stderr=PIPE, stdout=PIPE, creationflags=creationflags)
sys.exit(0)
