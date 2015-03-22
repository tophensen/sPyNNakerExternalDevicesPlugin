from spynnaker_external_devices_plugin.pyNN import ReverseIpTagMultiCastSource


class SpikeInjector(ReverseIpTagMultiCastSource):
    """ An Injector of Spikes for PyNN populations.  This only allows the user\
        to specify the virtual_key of the population to identify the population
    """

    def __init__(self, n_neurons, machine_time_step, timescale_factor,
                 spikes_per_second, ring_buffer_sigma, label, port,
                 virtual_key=None):
        ReverseIpTagMultiCastSource.__init__(
            self, port=port, label=label,
            n_neurons=n_neurons, machine_time_step=machine_time_step,
            ring_buffer_sigma=ring_buffer_sigma,
            timescale_factor=timescale_factor,
            spikes_per_second=spikes_per_second, virtual_key=virtual_key)
