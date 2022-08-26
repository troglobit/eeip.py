"""Created on 10.08.2022

@author: Joachim Wiberg

This is an example of how to verify heartbeat assemblies when running
against an OpENer-based open-source CIP adapter.

The heartbeat assembly uesd here is 254 and valid applicaiton-specific
assemblies are 100 and 101, respectively.

In Stage 1 the O->T produces assembly 101, length 154, with a standard
Real-Time header (run/idle flag).  The T->O produces an empty assembly,
i.e. heartbeat using instance 254.  The length of heartbeats is 0, but
when sending the Forward Open it is expected to send a length of two (2)
for the size of the CIP Sequence Number.

In Stage 2 the process is reversed, the T->O use assembly 100 instead.
Note, some customers require a Real-Time header also on the T->O data.
For those uses-cases, replace MODELESS with HEADER32BIT below.
"""
import argparse
import sys
import time
from eeip import *

parser = argparse.ArgumentParser()
parser.add_argument('-a', default='127.0.0.1', type=str, dest='address',
                    help='Address of adapter to connect to, default: 127.0.0.1')
parser.add_argument('-r', action='store_true', dest='t_o_runidle',
                    help='Expect Real-Time header on T->O for non-heartbeat assemblies')
args = parser.parse_args()

try:
    eeipclient = EEIPClient()
    print("Registering EtherNet/IP session.")
    eeipclient.register_session(args.address)
except ConnectionError as e:
    print("Failed connecting to " + args.address + ": " + str(e))
    sys.exit(1)
else:
    print("=== Stage 1: output 101, input 254");

# Parameters from Originator -> Target
eeipclient.o_t_instance_id = 101
eeipclient.o_t_length = 154
eeipclient.o_t_requested_packet_rate = 200000
eeipclient.o_t_realtime_format = RealTimeFormat.HEADER32BIT
eeipclient.o_t_owner_redundant = False
eeipclient.o_t_variable_length = False
eeipclient.o_t_connection_type = ConnectionType.POINT_TO_POINT

# Parameters from Target -> Originator
eeipclient.t_o_instance_id = 254
eeipclient.t_o_length = 0
eeipclient.t_o_requested_packet_rate = 200000
eeipclient.t_o_realtime_format = RealTimeFormat.HEARTBEAT
eeipclient.t_o_owner_redundant = False
eeipclient.t_o_variable_length = False
eeipclient.t_o_connection_type = ConnectionType.POINT_TO_POINT #ConnectionType.MULTICAST

try:
    eeipclient.forward_open()
except cip.CIPException as e:
    print("Failed Listen Only fwd open: " + str(e))
    eeipclient.unregister_session()
    sys.exit(1)
else:
    print("Waiting 2 sec before closing connection ...")
    time.sleep(2)
    print("Forward close.")
    eeipclient.forward_close()

print("Unregistering EtherNet/IP session.")
eeipclient.unregister_session()

# Wait a bit before next test phase
time.sleep(2)

print("=== Stage 2: output 254, input 100")
# Ip-Address of the Ethernet-IP Device (In this case Allen-Bradley 1734-AENT Point I/O)
# A Session has to be registered before any communication can be established
print("Registering EtherNet/IP session.")
eeipclient.register_session(args.address)

# Parameters from Originator -> Target
eeipclient.o_t_instance_id = 254 #101
eeipclient.o_t_length = 0 #154
eeipclient.o_t_requested_packet_rate = 200000  # Packet rate 200ms (default 500ms)
eeipclient.o_t_realtime_format = RealTimeFormat.HEARTBEAT #RealTimeFormat.HEADER32BIT
eeipclient.o_t_owner_redundant = False
eeipclient.o_t_variable_length = False
eeipclient.o_t_connection_type = ConnectionType.POINT_TO_POINT

# Parameters from Target -> Originator
eeipclient.t_o_instance_id = 100
eeipclient.t_o_length = 78
eeipclient.t_o_requested_packet_rate = 200000  # Packet rate 200ms (default 500ms)
if args.t_o_runidle:
    eeipclient.t_o_realtime_format = RealTimeFormat.HEADER32BIT
else:
    eeipclient.t_o_realtime_format = RealTimeFormat.MODELESS
eeipclient.t_o_owner_redundant = False
eeipclient.t_o_variable_length = False
eeipclient.t_o_connection_type = ConnectionType.MULTICAST #ConnectionType.POINT_TO_POINT

try:
    eeipclient.forward_open()
except cip.CIPException as e:
    print("Failed Input Only fwd open: " + str(e))
    eeipclient.unregister_session()
    sys.exit(1)
else:
    print("Waiting 2 sec before closing connection ...")
    time.sleep(2)
    print("Forward close.")
    eeipclient.forward_close()

print("Unregistering EtherNet/IP session.")
eeipclient.unregister_session()
print("Done.")
