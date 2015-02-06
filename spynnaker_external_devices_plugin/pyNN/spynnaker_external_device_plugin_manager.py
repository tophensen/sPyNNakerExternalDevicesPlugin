from pacman.model.partitionable_graph.partitionable_edge import \
    PartitionableEdge
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spynnaker.pyNN import get_spynnaker
from spinn_front_end_common.utility_models.live_packet_gather \
    import LivePacketGather


class SpynnakerExternalDevicePluginManager(object):

    def __init__(self):
        self._live_spike_recorders = dict()

    def add_edge_to_recorder_vertex(
            self, vertex_to_record_from, port, hostname, tag=None,
            strip_sdp=True, use_prefix=False, key_prefix=None,
            prefix_type=None, message_type=EIEIOTypeParam.KEY_32_BIT,
            right_shift=0, payload_as_time_stamps=True,
            use_payload_prefix=True, payload_prefix=None,
            payload_right_shift=0, number_of_packets_sent_per_time_step=0):

        _spinnaker = get_spynnaker()

        # locate the live spike recorder
        if (port, hostname) in self._live_spike_recorders:
            live_spike_recorder = self._live_spike_recorders[(port, hostname)]
        else:

            live_spike_recorder = LivePacketGather(
                _spinnaker.machine_time_step, _spinnaker.timescale_factor,
                tag, port, hostname, strip_sdp, use_prefix, key_prefix,
                prefix_type, message_type, right_shift, payload_as_time_stamps,
                use_payload_prefix, payload_prefix, payload_right_shift,
                number_of_packets_sent_per_time_step)
            self._live_spike_recorders[(port, hostname)] = live_spike_recorder
            _spinnaker.add_vertex(live_spike_recorder)

        # create the edge and add
        edge = PartitionableEdge(vertex_to_record_from,
                                 live_spike_recorder, "recorder_edge")
        _spinnaker.add_edge(edge)
