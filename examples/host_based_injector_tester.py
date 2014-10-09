from spinnman.transceiver import create_transceiver_from_hostname
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.connections.udp_connection import UDPConnection
number_of_packets = 34

udp_connection = UDPConnection(remote_host="spinn-1.cs.man.ac.uk",
                               remote_port="12345")

for packet in range(number_of_packets):
    data = bytearray()
    header = SDPHeader()
    message = SDPMessage(sdp_header=header, data=data)
    tx.send_message(message=message, response_required=False)