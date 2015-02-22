"""
The :py:mod:`spynnaker.pynn` package contains the frontend specifications
and implementation for the PyNN High-level API
(http://neuralensemble.org/trac/PyNN)
"""

# external models
from spinnman.messages.eieio.eieio_type_param import EIEIOTypeParam
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_cochlea_device import ExternalCochleaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_fpga_retina_device import ExternalFPGARetinaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_motor_device import MunichMotorDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_retina_device import MunichRetinaDevice
from spynnaker_external_devices_plugin.pyNN.control_models.\
    munich_motor_control import MunichMotorControl
from spynnaker_external_devices_plugin.pyNN.utility_models.\
    reverse_ip_tag_multi_cast_source import ReverseIpTagMultiCastSource
from spynnaker_external_devices_plugin.pyNN.utility_models.live_packet_gather \
    import LivePacketGather
from spynnaker_external_devices_plugin.pyNN.\
    spynnaker_external_device_plugin_manager import \
    SpynnakerExternalDevicePluginManager
from spynnaker.pyNN.utilities import conf

spynnaker_external_devices = SpynnakerExternalDevicePluginManager()


def activate_live_output_for(
        population, port=None, host=None, tag=None,
        strip_sdp=True, use_prefix=False, key_prefix=None,
        prefix_type=None, message_type=EIEIOTypeParam.KEY_32_BIT,
        right_shift=0, payload_as_time_stamps=True,
        use_payload_prefix=True, payload_prefix=None,
        payload_right_shift=0, number_of_packets_sent_per_time_step=0):

    # get default params if none set
    if port is None:
        port = conf.config.getint("Recording", "live_spike_port")
    if host is None:
        host = conf.config.get("Recording", "live_spike_host")
    if tag is None:
        tag = conf.config.getint("Recording", "live_spike_tag")

    # add new edge and vertex if required to spinnaker graph
    spynnaker_external_devices.add_edge_to_recorder_vertex(
        population._vertex, port, host, tag, strip_sdp, use_prefix,
        key_prefix, prefix_type, message_type, right_shift,
        payload_as_time_stamps, use_payload_prefix, payload_prefix,
        payload_right_shift, number_of_packets_sent_per_time_step)
