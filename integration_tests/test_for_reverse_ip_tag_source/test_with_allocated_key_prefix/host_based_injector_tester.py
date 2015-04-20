from spinnman.messages.eieio.data_messages.eieio_32bit.\
    eieio_32bit_data_message import EIEIO32BitDataMessage
from spynnaker.pyNN.utilities.conf import config
from spinnman.connections.udp_packet_connections.reverse_iptag_connection \
    import ReverseIPTagConnection

udp_connection = \
    ReverseIPTagConnection(remote_host=config.get("Machine", "machineName"),
                           remote_port=12345)

key = 0x70800
# key = 0x800
payload = 1


message = EIEIO32BitDataMessage()
message.add_key(key)
udp_connection.send_eieio_message(message)