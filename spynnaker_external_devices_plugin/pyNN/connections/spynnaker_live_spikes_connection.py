from spynnaker_external_devices_plugin.pyNN\
    .connections.spynnaker_database_connection \
    import SpynnakerDatabaseConnection
from spynnaker_external_devices_plugin.pyNN.connections\
    .spynnaker_sender_connection import SpynnakerSenderConnection

from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spinnman.messages.eieio.eieio_message import EIEIOMessage
from spinnman.messages.eieio.eieio_header import EIEIOHeader
from spinnman.connections.udp_packet_connections.stripped_iptag_connection \
    import StrippedIPTagConnection
from spinnman.constants import TRAFFIC_TYPE
from spinnman.data.little_endian_byte_array_byte_reader \
    import LittleEndianByteArrayByteReader

from threading import Thread

# The maximum number of 32-bit keys that will fit in a packet
_MAX_FULL_KEYS_PER_PACKET = 63

# The maximum number of 16-bit keys that will fit in a packet
_MAX_HALF_KEYS_PER_PACKET = 127


class SpynnakerLiveSpikesConnection(SpynnakerDatabaseConnection):
    """ A connection for receiving and sending live spikes from and to\
        SpiNNaker
    """

    def __init__(self, receive_labels=None, send_labels=None, local_host=None,
                 local_port=19999):
        """

        :param receive_labels: Labels of population from which live spikes\
                    will be received.
        :type receive_labels: iterable of str
        :param send_labels: Labels of population to which live spikes will be\
                    sent
        :type send_labels: iterable of str
        :param local_host: Optional specification of the local hostname or\
                    ip address of the interface to listen on
        :type local_host: str
        :param local_port: Optional specification of the local port to listen\
                    on.  Must match the port that the toolchain will send the\
                    notification on (19999 by default)
        :type local_port: int

        """

        SpynnakerDatabaseConnection.__init__(
            self, self._read_database_callback, self._start_callback,
            local_host=local_host, local_port=local_port)

        self._receive_labels = receive_labels
        self._send_labels = send_labels
        self._sender_connection = None
        self._send_address_details = dict()
        self._neuron_id_to_key = dict()
        self._key_to_neuron_id_and_label = dict()
        self._live_spike_callbacks = dict()
        self._start_callbacks = dict()
        if receive_labels is not None:
            for label in receive_labels:
                self._live_spike_callbacks[label] = list()
                self._start_callbacks[label] = list()
        if send_labels is not None:
            for label in send_labels:
                self._start_callbacks[label] = list()

    def add_receive_callback(self, label, live_spike_callback):
        """ Add a callback for the reception of live spikes from a population

        :param label: The label of the population to be notified about. Must\
                    be one of the populations listed in the constructor
        :type label: str
        :param spikes_callback_function: A function to be called when spikes\
                    are received.  This should take as parameters the label\
                    of the population, the simulation timestep when the spike\
                    occured, and an array-like of neuron ids.
        :type spikes_callback_function: function(str, int, [int]) -> None
        """
        self._live_spike_callbacks[label].append(live_spike_callback)

    def add_start_callback(self, label, start_callback):
        """ Add a callback for the start of the simulation

        :param start_callback_function: A function to be called when the start\
                    message has been received.  This function should take the\
                    label of the referenced population, and an instance of\
                    this class, which can be used to send spikes
        :type start_callback_function: function(str, \
                    :py:class:`SpynnakerLiveInputSpikesConnection`) -> None
        """
        self._start_callbacks[label].append(start_callback)

    def _read_database_callback(self, database_reader):
        if self._send_labels is not None:
            self._sender_connection = SpynnakerSenderConnection()
            for send_label in self._send_labels:
                ip_address, port = database_reader.get_live_input_details(
                    send_label)
                self._send_address_details[send_label] = (ip_address, port)
                self._neuron_id_to_key[send_label] = \
                    database_reader.get_neuron_id_to_key_mapping(send_label)
        if self._receive_labels is not None:
            receivers = dict()

            for receive_label in self._receive_labels:
                _, port, strip_sdp = database_reader.get_live_output_details(
                    receive_label)
                if strip_sdp:
                    if port not in receivers:
                        receivers[port] = StrippedIPTagConnection(
                            local_port=port)
                        receivers[port].register_callback(
                            self._receive_packet_callback,
                            TRAFFIC_TYPE.EIEIO_DATA)
                else:
                    raise Exception("Currently, only ip tags which strip the"
                                    " SDP headers are supported")

                key_to_neuron_id = \
                    database_reader.get_key_to_neuron_id_mapping(receive_label)
                for (key, neuron_id) in key_to_neuron_id.iteritems():
                    self._key_to_neuron_id_and_label[key] = (neuron_id,
                                                             receive_label)

    def _start_callback(self):
        for (label, callbacks) in self._start_callbacks.iteritems():
            for callback in callbacks:
                callback_thread = Thread(target=callback, args=(label, self),
                                         verbose=True)
                callback_thread.start()

    def _receive_packet_callback(self, packet):
        header = packet.eieio_header
        if not header.is_time:
            raise Exception(
                "Only packets with a timestamp are currently considered")

        time = 0
        if header.payload_base is not None:
            time = header.payload_base

        packet_type = header.type_param
        reader = LittleEndianByteArrayByteReader(packet.data)
        key_times_labels = dict()
        for _ in range(0, header.count_param + 1):
            next_time = time
            key = None
            label = None
            if packet_type == EIEIOTypeParam.KEY_16_BIT:
                key = reader.read_short()
            elif packet_type == EIEIOTypeParam.KEY_32_BIT:
                key = reader.read_int()
            elif packet_type == EIEIOTypeParam.KEY_PAYLOAD_16_BIT:
                key = reader.read_short()
                next_time = time | reader.read_short()
            elif packet_type == EIEIOTypeParam.KEY_PAYLOAD_32_BIT:
                key = reader.read_int()
                next_time = time | reader.read_int()
            if key in self._key_to_neuron_id_and_label:
                (neuron_id, label) = self._key_to_neuron_id_and_label[key]
                if (next_time, label) not in key_times_labels:
                    key_times_labels[(next_time, label)] = list()
                key_times_labels[(next_time, label)].append(neuron_id)

        for (key_time, label) in sorted(key_times_labels.keys()):
            for callback in self._live_spike_callbacks[label]:
                callback(label, key_time, key_times_labels[(key_time, label)])

    def send_spike(self, label, neuron_id, send_full_keys=False):
        """ Send a spike from a single neuron

        :param label: The label of the population from which the spike will\
                    originate
        :type label: str
        :param neuron_id: The id of the neuron sending a spike
        :type neuron_id: int
        :param send_full_keys: Determines whether to send full 32-bit keys,\
                    getting the key for each neuron from the database, or\
                    whether to send 16-bit neuron ids directly
        :type send_full_keys: bool
        """
        self.send_spikes(label, [neuron_id], send_full_keys)

    def send_spikes(self, label, neuron_ids, send_full_keys=False):
        """ Send a number of spikes

        :param label: The label of the population from which the spikes will\
                    originate
        :type label: str
        :param neuron_ids: array-like of neuron ids sending spikes
        :type: [int]
        :param send_full_keys: Determines whether to send full 32-bit keys,\
                    getting the key for each neuron from the database, or\
                    whether to send 16-bit neuron ids directly
        :type send_full_keys: bool
        """
        max_keys = _MAX_HALF_KEYS_PER_PACKET
        if send_full_keys:
            max_keys = _MAX_FULL_KEYS_PER_PACKET

        pos = 0
        while pos < len(neuron_ids):

            message = EIEIOMessage(EIEIOHeader(EIEIOTypeParam.KEY_32_BIT))

            spikes_in_packet = 0
            while (pos < len(neuron_ids) and spikes_in_packet < max_keys):
                key = neuron_ids[pos]
                if send_full_keys:
                    key = self._neuron_id_to_key[label][key]
                message.write_data(key)
                pos += 1
                spikes_in_packet += 1
            ip_address, port = self._send_address_details[label]
            self._sender_connection.send_eieio_message(message, ip_address,
                                                       port)