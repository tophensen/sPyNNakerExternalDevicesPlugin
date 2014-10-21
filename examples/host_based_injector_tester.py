from spinnman.messages.eieio.eieio_header import EIEIOHeader
from spinnman.messages.eieio.eieio_message import EIEIOMessage
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spinnman.messages.eieio.eieio_prefix_type import EIEIOPrefixType
from spinnman.connections.udp_packet_connections.reverse_iptag_connection import ReverseIPTagConnection
number_of_packets = 5

udp_connection = ReverseIPTagConnection(remote_host="spinn-9.cs.man.ac.uk",
                               remote_port=12345)

key = 1
payload = 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_16_BIT, count_param=1)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_16_BIT, count_param=1)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_16_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_16_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_16_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_16_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_16_BIT, count_param=1, prefix_param=0xfff0, payload_base=0xeee0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_16_BIT, count_param=1, prefix_param=0xfff0, payload_base=0xeee0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_32_BIT, count_param=1)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_32_BIT, count_param=1)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_32_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_32_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_32_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_32_BIT, count_param=1, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_32_BIT, count_param=1, prefix_param=0xfff0, payload_base=0xeeee0000, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key(key)
udp_connection.send_eieio_message(message)
key += 1

header = EIEIOHeader(type_param=EIEIOTypeParam.KEY_PAYLOAD_32_BIT, count_param=1, prefix_param=0xfff0, payload_base=0xeeee0000, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIOMessage(eieio_header=header, data=bytearray())
message.write_key_and_payload(key, payload)
udp_connection.send_eieio_message(message)
key += 1
payload += 1



#class EIEIOHeader(object):
#
#    def __init__(self, type_param, count_param, tag_param=0, prefix_param=None,
#                 payload_base=None, prefix_type=None, is_time=False):

#prefix_type
#class EIEIOPrefixType(Enum):
#    """ eieio type Flag for the message
#    """
#    LOWER_HALF_WORD = (0, "apply prefix on lower half of the word")
#    UPPER_HALF_WORD = (1, "apply prefix on top half of the word")

#EIEIOMessage(AbstractEIEIOMessage):
#
#    def __init__(self, eieio_header, data=bytearray()):
#        AbstractEIEIOMessage.__init__(self, data)
#        self._eieio_header = eieio_header

