from spinn_front_end_common.utility_models.reverse_ip_tag_multi_cast_source \
    import ReverseIpTagMultiCastSource


class UdpSpikeSource(ReverseIpTagMultiCastSource):
    """ Interface between PyNN Neural Models and Multicast Input that assumes
        that the input represents spikes.  This also adds the
        parameters required by the pyNN interface; these are not used.
    """

    def __init__(self, n_neurons, machine_time_step, timescale_factor,
                 spikes_per_second, ring_buffer_sigma, host_port_number,
                 host_ip_address, virtual_key, label, check_key=True,
                 prefix=None, prefix_type=None, tag=None, key_left_shift=0):
        ReverseIpTagMultiCastSource.__init__(
            self, n_neurons, machine_time_step, timescale_factor,
            host_port_number, host_ip_address, virtual_key, label,
            check_key=check_key, prefix=prefix, prefix_type=prefix_type,
            tag=tag, key_left_shift=key_left_shift)
