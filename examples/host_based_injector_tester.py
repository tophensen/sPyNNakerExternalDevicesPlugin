from spinnman.connections.udp_connection import UDPConnection
from spinnman.messages.eidio.eidio_header import EIDIOHeader
from spinnman.messages.eidio.eidio_message import EIDIOMessage
from spinnman.messages.eidio.eidio_type_param import EIDIOTypeParam

number_of_packets = 5

udp_connection = UDPConnection(remote_host="spinn-1.cs.man.ac.uk",
                               remote_port=12345)

for _ in range(number_of_packets):
    data = bytearray()
    data.append(0)
    data.append(7)
    header = EIDIOHeader(type_param=EIDIOTypeParam.KEY_16_BIT, count_param=1)
    message = EIDIOMessage(eidio_header=header, data=data)
    udp_connection.send_eidio_message(message)

for _ in range(number_of_packets):
    data = bytearray()
    data.append(0)
    data.append(7)
    data = bytearray()
    data.append(0)
    data.append(7)
    header = EIDIOHeader(type_param=EIDIOTypeParam.KEY_PAYLOAD_16_BIT, count_param=2)
    message = EIDIOMessage(eidio_header=header, data=data)
    udp_connection.send_eidio_message(message)