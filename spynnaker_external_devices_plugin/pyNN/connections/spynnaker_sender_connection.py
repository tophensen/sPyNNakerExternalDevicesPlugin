from spinnman.connections.udp_packet_connections.udp_connection \
    import UDPConnection


import logging

logger = logging.getLogger(__name__)


class SpynnakerSenderConnection(UDPConnection):
    """ A connection for sending EIEIO messages to multiple places with a\
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

    def send_eieio_message(self, eieio_message, ip_address, port):
        self.send_to(eieio_message.bytestring, (ip_address, port))
