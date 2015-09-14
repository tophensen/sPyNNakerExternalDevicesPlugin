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
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    pushbot_retina_device import PushBotRetinaDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    pushbot_retina_device import PushBotRetinaResolution
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    pushbot_retina_device import PushBotRetinaPolarity
from spynnaker_external_devices_plugin.pyNN import model_binaries
from spynnaker_external_devices_plugin.pyNN.\
    spynnaker_external_device_plugin_manager import \
    SpynnakerExternalDevicePluginManager
from spynnaker_external_devices_plugin.pyNN.utility_models.spike_injector \
    import SpikeInjector as SpynnakerExternalDeviceSpikeInjector
from spynnaker_external_devices_plugin.pyNN.connections\
    .spynnaker_live_spikes_connection import SpynnakerLiveSpikesConnection

from spynnaker.pyNN.utilities import conf
from spynnaker.pyNN import IF_curr_exp
from spynnaker.pyNN.spinnaker import executable_finder

from spinn_front_end_common.utilities.notification_protocol.socket_address \
    import SocketAddress

import os

executable_finder.add_path(os.path.dirname(model_binaries.__file__))
spynnaker_external_devices = SpynnakerExternalDevicePluginManager()


def activate_live_output_for(
        population, database_notify_host=None, database_notify_port_num=None,
        database_ack_port_num=None, board_address=None, port=None,
        host=None, tag=None, strip_sdp=True, use_prefix=False, key_prefix=None,
        prefix_type=None, message_type=EIEIOType.KEY_32_BIT,
        right_shift=0, payload_as_time_stamps=True,
        use_payload_prefix=True, payload_prefix=None,
        payload_right_shift=0, number_of_packets_sent_per_time_step=0):
    """ Output the spikes from a given population from SpiNNaker as they
        occur in the simulation

    :param population: The population to activate the live output for
    :type population: Population
    :param database_notify_host: the hostnmae for the device which is listening
    to the database notifcation.
    :type database_notify_host: str
    :param database_ack_port_num: the port number to which a external device
    will ack that they have finished reading the database and are ready for
    it to start execution
    :type database_ack_port_num: int
    :param database_notify_port_num: The port number to which a external device
    will recieve the database is ready command
    :type database_notify_port_num: int
    :param board_address: A fixed board address required for the tag, or\
                    None if any address is OK
    :type board_address: str
    :param key_prefix: the prefix to be applied to the key
    :type key_prefix: int or None
    :param prefix_type: if the prefix type is 32 bit or 16 bit
    :param message_type: if the message is a eieio_command mesage, or
    eieio data message with 16 bit or 32 bit keys.
    :param payload_as_time_stamps:
    :param right_shift:
    :param use_payload_prefix:
    :param payload_prefix:
    :param payload_right_shift:
    :param number_of_packets_sent_per_time_step:

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
    # get default params for the database socket if required

    if database_notify_port_num is None:
        database_notify_port_num = conf.config.getint("Database",
                                                      "notify_port")
    if database_notify_host is None:
        database_notify_host = conf.config.get("Database", "notify_hostname")
    if database_ack_port_num is None:
        database_ack_port_num = conf.config.get("Database", "listen_port")
        if database_ack_port_num == "None":
            database_ack_port_num = None

    # add new edge and vertex if required to spinnaker graph
    spynnaker_external_devices.add_edge_to_recorder_vertex(
        population._vertex, port, host, tag, board_address, strip_sdp,
        use_prefix, key_prefix, prefix_type, message_type, right_shift,
        payload_as_time_stamps, use_payload_prefix, payload_prefix,
        payload_right_shift, number_of_packets_sent_per_time_step)
    # build the database socket address used by the notifcation interface
    database_socket = SocketAddress(
        listen_port=database_ack_port_num,
        notify_host_name=database_notify_host,
        notify_port_no=database_notify_port_num)
    # update socket interface with new demands.
    spynnaker_external_devices.add_socket_address(database_socket)


def activate_live_output_to(population, device):
    """ Activate the output of spikes from a population to an external device.\
        Note that all spikes will be sent to the device.

    :param population: The pyNN population object from which spikes will be\
                sent.
    :param device: The pyNN population external device to which the spikes\
                will be sent.
    """
    spynnaker_external_devices.add_edge(
        population._get_vertex, device._get_vertex)


def MunichMotorPopulation(
        spinnaker_link_id, speed=30, sample_time=4096, update_time=512,
        delay_time=5, delta_threshold=23, continue_if_not_different=True,
        model=IF_curr_exp, params=None):
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

    :param spinnaker_link_id: the id for the spinnaker link
    :type spinnaker_link_id: int
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
    :type params: dict or None
    :return: The newly created population
    :rtype: Population
    """
    # checker for params and not having the setter for mutliple versions of
    # munich motor control having cloned data
    if params is None:
        params = {}
    return spynnaker_external_devices.create_munich_motor_population(
        spinnaker_link_id, speed, sample_time, update_time, delay_time,
        delta_threshold, continue_if_not_different, model, params)


def SpikeInjector(
        n_neurons, machine_time_step, timescale_factor, spikes_per_second,
        ring_buffer_sigma, label, port, virtual_key=None,
        database_notify_host=None, database_notify_port_num=None,
        database_ack_port_num=None):
    """
    supports adding a spike injector to the applciation graph.
    :param n_neurons: the number of neurons the spike injector will emulate
    :type n_neurons: int
    :param machine_time_step: the time period in ms for each timer callback
    :type machine_time_step: int
    :param timescale_factor: the amount of scaling needed of the machine time
    step (basically a slow down function)
    :type timescale_factor: int
    :param spikes_per_second: the expected number of spikes per second
    :type spikes_per_second: int
    :param ring_buffer_sigma: the number of standard divations from a
    calcuation on how much safety in percision vs overflowing
     (this is deduced from the front end)
    :type ring_buffer_sigma: int
    :param label: the label given to the population
    :type label: str
    :param port: the port number used to listen for injections of spikes
    :type port: int
    :param virtual_key: the virtual key used in the routing system
    :type virtual_key: int
    :param database_notify_host: the hostnmae for the device which is listening
    to the database notifcation.
    :type database_notify_host: str
    :param database_ack_port_num: the port number to which a external device
    will ack that they have finished reading the database and are ready for
    it to start execution
    :type database_ack_port_num: int
    :param database_notify_port_num: The port number to which a external device
    will recieve the database is ready command
    :type database_notify_port_num: int

    :return:
    """
    if database_notify_port_num is None:
        database_notify_port_num = conf.config.getint("Database",
                                                      "notify_port")
    if database_notify_host is None:
        database_notify_host = conf.config.get("Database", "notify_hostname")
    if database_ack_port_num is None:
        database_ack_port_num = conf.config.get("Database", "listen_port")
        if database_ack_port_num == "None":
            database_ack_port_num = None

    # build the database socket address used by the notifcation interface
    database_socket = SocketAddress(
        listen_port=database_ack_port_num,
        notify_host_name=database_notify_host,
        notify_port_no=database_notify_port_num)
    # update socket interface with new demands.
    spynnaker_external_devices.add_socket_address(database_socket)
    return SpynnakerExternalDeviceSpikeInjector(
        n_neurons=n_neurons, machine_time_step=machine_time_step,
        timescale_factor=timescale_factor, spikes_per_second=spikes_per_second,
        ring_buffer_sigma=ring_buffer_sigma, label=label, port=port,
        virtual_key=virtual_key)
