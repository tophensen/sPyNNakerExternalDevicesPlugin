from spinnman.connections.udp_connection import UDPConnection
from spinnman.messages.eieio.eieio_header import EIEIOHeader
from spinnman.messages.eieio.eieio_message import EIEIOMessage
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
import struct

number_of_packets = 5

udp_connection = UDPConnection(remote_host="spinn-9.cs.man.ac.uk",
                               remote_port=12345)

for _ in range(number_of_packets):
    data = bytearray(struct.pack("<H", 0x18))
#    data = bytearray()
#    data.append(0)
#    data.append(7)
    header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_16_BIT, count_param=1)
    message = EIEIOMessage(eieio_header=header, data=data)
    udp_connection.send_eieio_message(message)

for _ in range(number_of_packets):
    data = bytearray(struct.pack("<H", 7))
    data += bytearray(struct.pack("<H", 7))

    header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_16_BIT,
                         count_param=2)
    message = EIEIOMessage(eieio_header=header, data=data)
    udp_connection.send_eieio_message(message)