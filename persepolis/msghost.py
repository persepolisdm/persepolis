# Windows message host middle man. 
# Use pyinstaller to create a single-file executable from this file.
# Then place it in installation root directory.

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



creationflags = CREATE_BREAKAWAY_FROM_JOB | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

cwd = sys.argv[0]
current_directory = os.path.dirname(cwd)
persepolis_path = os.path.join(current_directory, "Persepolis Download Manager.exe")

## TODO: this fix is a temporary solution
## Both firefox and Chrome messages from stdin will be parsed successfully in this file.
## But if you skip parsing and redirect them to pdm by Popen(...,stdin=None,...):
## - message from firefox will be redirected to persepolis with no problem.
## - message from Chrome will be dropped and pdm will see no message.
## As a temporary solution, message is parsed here and saved to a binary object.
## Then this binary object is passed to pdm.

raw_size = sys.stdin.buffer.read(4) 
length = struct.unpack('@I', raw_size)[0]
raw_data = sys.stdin.buffer.read(length)
received_message = struct.pack("=I{}s".format(length), length, raw_data)

# pass '--nhm' to ensure there will be an unknown arg in parse_args 
# to trigger parsing NHM messages
command = [os.path.abspath(persepolis_path), "--nhm"]
proc = Popen(command, stdin=PIPE, stderr=PIPE, stdout=PIPE, creationflags=creationflags)
proc.communicate(input=received_message)
sys.exit(0)
