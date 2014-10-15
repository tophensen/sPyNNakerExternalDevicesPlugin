from spinnman.connections.udp_connection import UDPConnection
from spinnman.messages.eieio.eieio_header import EIEIOHeader
from spinnman.messages.eieio.eieio_message import EIEIOMessage
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
import struct

number_of_packets = 5

udp_connection = UDPConnection(remote_host="spinn-9.cs.man.ac.uk",
                               remote_port=12345)

for _ in range(number_of_packets):
    header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_16_BIT, count_param=1)
    message = EIEIOMessage(eieio_header=header)
    message.write_key(0x18)
    udp_connection.send_eieio_message(message)

#class EIEIOHeader(object):
#
#    def __init__(self, type_param, count_param, tag_param=0, prefix_param=None,
#                 payload_base=None, prefix_type=None, is_time=False):

#EIEIOMessage(AbstractEIEIOMessage):
#
#    def __init__(self, eieio_header, data=bytearray()):
#        AbstractEIEIOMessage.__init__(self, data)
#        self._eieio_header = eieio_header

