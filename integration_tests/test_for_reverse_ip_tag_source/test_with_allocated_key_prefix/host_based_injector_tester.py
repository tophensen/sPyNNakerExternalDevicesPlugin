from spinnman.messages.eieio.data_messages.eieio_data_header import EIEIODataHeader
from spinnman.messages.eieio.data_messages.eieio_data_message import EIEIODataMessage
from spinnman.messages.eieio.eieio_type import EIEIOType
from spynnaker.pyNN.utilities.conf import config
from spinnman.connections.udp_packet_connections.reverse_iptag_connection \
    import ReverseIPTagConnection

udp_connection = \
    ReverseIPTagConnection(remote_host=config.get("Machine", "machineName"),
                           remote_port=12345)

key = 0x70800
#key = 0x800
payload = 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_32_BIT)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
udp_connection.send_eieio_message(message)
key += 1

'''
header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_16_BIT)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_16_BIT, prefix_param=0xfff0,
                     prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
injection_connection.send_eieio_message(message)
key += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_16_BIT,
                     prefix_param=0xfff0,
                     prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_16_BIT,
                     prefix_param=0xfff0,
                     prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
injection_connection.send_eieio_message(message)
key += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_16_BIT, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_16_BIT, prefix_param=0xfff0, payload_base=0xeee0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
injection_connection.send_eieio_message(message)
key += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_16_BIT, prefix_param=0xfff0, payload_base=0xeee0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_32_BIT)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
injection_connection.send_eieio_message(message)
key += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_32_BIT)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_32_BIT, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
injection_connection.send_eieio_message(message)
key += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_32_BIT, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.UPPER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_32_BIT, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
injection_connection.send_eieio_message(message)
key += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_32_BIT, prefix_param=0xfff0, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_32_BIT, prefix_param=0xfff0, payload_base=0xeeee0000, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key)
injection_connection.send_eieio_message(message)
key += 1

header = EIEIODataHeader(type_param=EIEIOType.KEY_PAYLOAD_32_BIT, prefix_param=0xfff0, payload_base=0xeeee0000, prefix_type=EIEIOPrefixType.LOWER_HALF_WORD)
message = EIEIODataMessage(eieio_header=header, data=bytearray())
message.write_data(key, payload)
injection_connection.send_eieio_message(message)
key += 1
payload += 1



#class EIEIODataHeader(object):
#
#    def __init__(self, type_param, count_param, tag_param=0, prefix_param=None,
#                 payload_base=None, prefix_type=None, is_time=False):

#prefix_type
#class EIEIOPrefixType(Enum):
#    """ eieio type Flag for the message
#    """
#    LOWER_HALF_WORD = (0, "apply prefix on lower half of the word")
#    UPPER_HALF_WORD = (1, "apply prefix on top half of the word")

#EIEIODataMessage(AbstractEIEIOMessage):
#
#    def __init__(self, eieio_header, data=bytearray()):
#        AbstractEIEIOMessage.__init__(self, data)
#        self._eieio_header = eieio_header

'''