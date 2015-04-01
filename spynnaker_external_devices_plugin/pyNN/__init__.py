"""
The :py:mod:`spynnaker.pynn` package contains the frontend specifications
and implementation for the PyNN High-level API
(http://neuralensemble.org/trac/PyNN)
"""

from spinnman.messages.eieio.eieio_type import EIEIOType

from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_cochlea_device import ExternalCochleaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    external_fpga_retina_device import ExternalFPGARetinaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_retina_device import MunichRetinaDevice
from spynnaker_external_devices_plugin.pyNN.utility_models.spike_injector \
    import SpikeInjector
from spynnaker_external_devices_plugin.pyNN import model_binaries
from spynnaker_external_devices_plugin.pyNN.\
    spynnaker_external_device_plugin_manager import \
    SpynnakerExternalDevicePluginManager

from spynnaker.pyNN.utilities import conf
from spynnaker.pyNN import IF_curr_exp
from spynnaker.pyNN.spinnaker import executable_finder

from spinn_front_end_common.utility_models.live_packet_gather \
    import LivePacketGather

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


def MunichMotorPopulation(
        virtual_chip_x, virtual_chip_y, connected_to_real_chip_x,
        connected_to_real_chip_y, connected_to_real_chip_link_id, speed=30,
        sample_time=4096, update_time=512, delay_time=5,
        delta_threshold=23, continue_if_not_different=True,
        model=IF_curr_exp, params={}):
    """ Create a population of 6 neurons which will drive the robot motor.
        Neuron id 0 drives the forwards direction
                  1 drives the backwards direction
                  2 drives the left direction
                  3 drives the right direction
                  4 drives the clockwise direction
                  5 drives the counter-clockwise direction
        The control works by counting the number of spikes sent to each\
        neuron, and then taking the difference between opposite\
        directions at every sample time timesteps.  If the difference is\
        above the threshold, a command is sent to move the robot in the\
        appropriate direction.
        The robot currently needs to be assigned a "virtual chip", which\
        is then used to determine the routing keys that will be used for\
        the motor control.  This chip must be one which does not exist\
        within the current physical machine.

    :param virtual_chip_x: The x coordinate of the virtual chip
    :type virtual_chip_x: int
    :param virtual_chip_y: The y coordinate of the virtual chip
    :type virtual_chip_y: int
    :param connected_to_real_chip_x: The x coordinate of the real chip in\
                the machine where the spinn-link is connected
    :type connected_to_real_chip_x: int
    :param connected_to_real_chip_y: The y coordinate of the real chip in\
                the machine where the spinn-link is connected
    :type connected_to_real_chip_x: int
    :param connected_to_real_chip_link_id: The id of the link on the real\
                chip where the spinn-link is connected
    :type connected_to_real_chip_link_id: int
    :param speed: The speed to be sent to the motor when a direction is\
                activated
    :type speed: int
    :param sample_time: The number of time steps between samples of the\
                spike counts to determine the motor direction
    :type sample_time: int
    :param update_time: The number of time steps between sending updates\
                of the motor speed
    :type update_time: int
    :param delay_time: The minimum number of microseconds between commands\
                sent to the robot
    :type delay_time: int
    :param delta_threshold: The threshold of the difference between spike\
                counts of opposite directions over which a direction will\
                be chosen
    :type delta_threshold: int
    :param continue_if_not_different: Determines if the robot should\
                continue in the current direction until a new direction\
                is chosen, or if it should only move for one period\
                before stopping unless the same direction is chosen\
                again
    :type continue_if_not_different: bool
    :param model: The neuron model to use for the pre-motor population
    :type model: class
    :param params: Dictionary of parameters to give to the model
    :type params: dict
    :return: The newly created population
    :rtype: Population
    """
    return spynnaker_external_devices.create_munich_motor_population(
        virtual_chip_x, virtual_chip_y, connected_to_real_chip_x,
        connected_to_real_chip_y, connected_to_real_chip_link_id, speed,
        sample_time, update_time, delay_time, delta_threshold,
        continue_if_not_different, model, params)
