"""
The :py:mod:`spynnaker.pynn` package contains the frontend specifications
and implementation for the PyNN High-level API
(http://neuralensemble.org/trac/PyNN)
"""

# external models
from spinnman.messages.eieio.eieio_type import EIEIOType
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_cochlea_device import ExternalCochleaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_fpga_retina_device import ExternalFPGARetinaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_retina_device import MunichRetinaDevice
from spynnaker_external_devices_plugin.pyNN.utility_models.spike_injector \
    import SpikeInjector
from spinn_front_end_common.utility_models.live_packet_gather \
    import LivePacketGather
from spynnaker_external_devices_plugin.pyNN import model_binaries
from spynnaker_external_devices_plugin.pyNN.\
    spynnaker_external_device_plugin_manager import \
    SpynnakerExternalDevicePluginManager
from spynnaker.pyNN.utilities import conf
from spynnaker.pyNN.spinnaker import executable_finder

import os

executable_finder.add_path(os.path.dirname(model_binaries.__file__))
spynnaker_external_devices = SpynnakerExternalDevicePluginManager()


def activate_live_output_for(
        population, board_address=None, port=None, host=None, tag=None,
        strip_sdp=True, use_prefix=False, key_prefix=None,
        prefix_type=None, message_type=EIEIOType.KEY_32_BIT,
        right_shift=0, payload_as_time_stamps=True,
        use_payload_prefix=True, payload_prefix=None,
        payload_right_shift=0, number_of_packets_sent_per_time_step=0):
    """ Output the spikes from a given population from SpiNNaker as they
        occur in the simulation

    :param population: The population to activate the live output for
    :type population: Population
    :param port: The UDP port to which the live spikes will be sent.  If not\
                specified, the port will be taken from the "live_spike_port"\
                parameter in the "Recording" section of the spynnaker cfg file.
    :type port: int
    :param host: The host name or IP address to which the live spikes will be\
                sent.  If not specified, the host will be taken from the\
                "live_spike_host" parameter in the "Recording" section of the\
                spynnaker cfg file.
    :type host: str
    :param tag: The IP tag to be used for the spikes.  If not specified, one\
                will be automatically assigned
    :type tag: int
    :param strip_sdp: Determines if the SDP headers will be stripped from the\
                transmitted packet.
    :type strip_sdp: bool
    :param use_prefix: Determines if the spike packet will contain a common\
                prefix for the spikes
    :type use_prefix: bool
    """

    # get default params if none set
    if port is None:
        port = conf.config.getint("Recording", "live_spike_port")
    if host is None:
        host = conf.config.get("Recording", "live_spike_host")

    # add new edge and vertex if required to spinnaker graph
    spynnaker_external_devices.add_edge_to_recorder_vertex(
        population._vertex, port, host, tag, board_address, strip_sdp,
        use_prefix, key_prefix, prefix_type, message_type, right_shift,
        payload_as_time_stamps, use_payload_prefix, payload_prefix,
        payload_right_shift, number_of_packets_sent_per_time_step)
