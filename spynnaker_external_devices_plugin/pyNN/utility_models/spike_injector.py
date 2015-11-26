from spinn_front_end_common.abstract_models.\
    abstract_provides_outgoing_edge_constraints import \
    AbstractProvidesOutgoingEdgeConstraints
from spinn_front_end_common.utility_models.reverse_ip_tag_multi_cast_source\
    import ReverseIpTagMultiCastSource
from spinn_front_end_common.utility_models\
    .reverse_ip_tag_multicast_source_partitioned_vertex \
    import ReverseIPTagMulticastSourcePartitionedVertex

from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_contiguous_range_constraint \
    import KeyAllocatorContiguousRangeContraint

from spynnaker.pyNN.models.common.abstract_spike_recordable\
    import AbstractSpikeRecordable
from spynnaker.pyNN.utilities import constants
from spynnaker.pyNN.utilities.conf import config
from spynnaker.pyNN.models.common.eieio_spike_recorder \
    import EIEIOSpikeRecorder


class SpikeInjector(ReverseIpTagMultiCastSource,
                    AbstractProvidesOutgoingEdgeConstraints,
                    AbstractSpikeRecordable):
    """ An Injector of Spikes for PyNN populations.  This only allows the user\
        to specify the virtual_key of the population to identify the population
    """

    def __init__(
            self, n_neurons, machine_time_step, timescale_factor, label, port,
            virtual_key=None, spike_buffer_max_size=(
                constants.EIEIO_SPIKE_BUFFER_SIZE_BUFFERING_OUT),
            buffer_size_before_receive=(
                constants.EIEIO_BUFFER_SIZE_BEFORE_RECEIVE)):

        ReverseIpTagMultiCastSource.__init__(
            self, n_keys=n_neurons, machine_time_step=machine_time_step,
            timescale_factor=timescale_factor, label=label, receive_port=port,
            virtual_key=virtual_key)

        # Set up for recording
        self._spike_recorder = EIEIOSpikeRecorder(machine_time_step)
        self._spike_buffer_max_size = spike_buffer_max_size
        self._buffer_size_before_receive = buffer_size_before_receive

    def is_recording_spikes(self):
        return self._spike_recorder.record

    def set_recording_spikes(self):
        ip_address = config.get("Buffers", "receive_buffer_host")
        port = config.getint("Buffers", "receive_buffer_port")
        self.enable_recording(
            ip_address, port, None, None,
            self._spike_buffer_max_size,
            self._buffer_size_before_receive)
        self._spike_recorder.record = True

    def get_spikes(self, placements, graph_mapper):
        subvertices = graph_mapper.get_subvertices_from_vertex(self)
        buffer_manager = next(iter(subvertices)).buffer_manager
        return self._spike_recorder.get_spikes(
            self.label, buffer_manager,
            (ReverseIPTagMulticastSourcePartitionedVertex.
             _REGIONS.RECORDING_BUFFER.value),
            (ReverseIPTagMulticastSourcePartitionedVertex.
             _REGIONS.RECORDING_BUFFER_STATE.value),
            placements, graph_mapper, self,
            lambda subvertex: subvertex.virtual_key)

    def get_outgoing_edge_constraints(self, partitioned_edge, graph_mapper):
        constraints = ReverseIpTagMultiCastSource\
            .get_outgoing_edge_constraints(
                self, partitioned_edge, graph_mapper)
        constraints.append(KeyAllocatorContiguousRangeContraint())
        return constraints
