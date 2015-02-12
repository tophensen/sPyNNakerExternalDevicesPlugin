from spynnaker_external_devices_plugin.pyNN import ReverseIpTagMultiCastSource
from spynnaker.pyNN.utilities.conf import config


class SpikeInjector(ReverseIpTagMultiCastSource):

    def __init__(self, n_neurons, machine_time_step, timescale_factor,
                 spikes_per_second, ring_buffer_sigma, label, virtual_key=None,
                 port_number=None):
        if port_number is None:
            port_number = config.get("Injection", "default_port")
        ReverseIpTagMultiCastSource.__init__(
            self, host_port_number=port_number, label=label,
            n_neurons=n_neurons, machine_time_step=machine_time_step,
            ring_buffer_sigma=ring_buffer_sigma,
            timescale_factor=timescale_factor,
            spikes_per_second=spikes_per_second, virtual_key=virtual_key)
