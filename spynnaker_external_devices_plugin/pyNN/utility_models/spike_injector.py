from spinn_front_end_common.utility_models.reverse_ip_tag_multi_cast_source\
    import ReverseIpTagMultiCastSource
from spinn_front_end_common.abstract_models\
    .abstract_outgoing_edge_same_contiguous_keys_restrictor\
    import AbstractOutgoingEdgeSameContiguousKeysRestrictor


class SpikeInjector(ReverseIpTagMultiCastSource,
                    AbstractOutgoingEdgeSameContiguousKeysRestrictor):
    """ An Injector of Spikes for PyNN populations.  This only allows the user\
        to specify the virtual_key of the population to identify the population
    """

    def __init__(self, n_neurons, machine_time_step, timescale_factor,
                 spikes_per_second, ring_buffer_sigma, label, port,
                 virtual_key=None):
        ReverseIpTagMultiCastSource.__init__(
            self, port=port, label=label,
            n_neurons=n_neurons, machine_time_step=machine_time_step,
            timescale_factor=timescale_factor, virtual_key=virtual_key)
        AbstractOutgoingEdgeSameContiguousKeysRestrictor.__init__(self)

    def get_outgoing_edge_constraints(self, partitioned_edge, graph_mapper):
        constraints = (ReverseIpTagMultiCastSource
                       .get_outgoing_edge_constraints(
                           self, partitioned_edge, graph_mapper))
        constraints.extend(AbstractOutgoingEdgeSameContiguousKeysRestrictor
                           .get_outgoing_edge_constraints(
                               self, partitioned_edge, graph_mapper))
        return constraints
