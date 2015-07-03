from spinnman.constants import CONNECTION_TYPE
from spinnman.data.little_endian_byte_array_byte_writer\
    import LittleEndianByteArrayByteWriter
from spinnman.connections.udp_packet_connections.udp_connection \
    import UDPConnection


import logging

logger = logging.getLogger(__name__)


class SpynnakerSenderConnection(UDPConnection):
    """ A connection for sending eieio messages to multiple places with a\
        single connection
    """

    def __init__(self, local_host=None, local_port=None):
        """
        :param local_host: Optional specification of the local hostname or\
                    ip address of the interface to bind to
        :type local_host: str
        :param local_port: Optional specification of the local port to bind to
        :type local_port: int
        """
        UDPConnection.__init__(
            self, local_host=local_host, local_port=local_port,
            remote_host=None, remote_port=None)

    def connection_type(self):
        CONNECTION_TYPE.UDP_IPTAG

    def supports_sends_message(self, message):
        return True

    def send_eieio_message(self, eieio_message, ip_address, port):
        writer = LittleEndianByteArrayByteWriter()
        eieio_message.write_eieio_message(writer)
        self._socket.sendto(writer.data, (ip_address, port))
