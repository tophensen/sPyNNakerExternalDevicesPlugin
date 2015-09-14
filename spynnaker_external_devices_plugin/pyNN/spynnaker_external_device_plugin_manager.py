from pacman.model.partitionable_graph.multi_cast_partitionable_edge\
    import MultiCastPartitionableEdge
from spinnman.messages.eieio.eieio_type import EIEIOType
from spynnaker.pyNN import get_spynnaker
from spynnaker.pyNN import IF_curr_exp
from spynnaker_external_devices_plugin.pyNN\
    .control_models.munich_motor_control import MunichMotorControl
from spynnaker.pyNN.models.pynn_population import Population
from spinn_front_end_common.utility_models.live_packet_gather \
    import LivePacketGather


class SpynnakerExternalDevicePluginManager(object):

    def __init__(self):
        self._live_spike_recorders = dict()

    def add_socket_address(self, socket_address):
        """
        helper method for adding a socket address to the list needed to be
        checked by the notifcation protocol
        :param socket_address: the socket address
        :type socket_address:
        :return:
        """
        _spinnaker = get_spynnaker()
        _spinnaker._add_socket_address(socket_address)

    def add_edge_to_recorder_vertex(
            self, vertex_to_record_from, port, hostname, tag=None,
            board_address=None,
            strip_sdp=True, use_prefix=False, key_prefix=None,
            prefix_type=None, message_type=EIEIOType.KEY_32_BIT,
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
                hostname, port, board_address, tag, strip_sdp, use_prefix,
                key_prefix, prefix_type, message_type, right_shift,
                payload_as_time_stamps, use_payload_prefix, payload_prefix,
                payload_right_shift, number_of_packets_sent_per_time_step,
                label="LiveSpikeReceiver")
            self._live_spike_recorders[(port, hostname)] = live_spike_recorder
            _spinnaker.add_vertex(live_spike_recorder)

        # create the edge and add
        edge = MultiCastPartitionableEdge(
            vertex_to_record_from, live_spike_recorder, label="recorder_edge")
        _spinnaker.add_edge(edge)

    def add_edge(self, vertex, device_vertex):
        _spinnaker = get_spynnaker()
        edge = MultiCastPartitionableEdge(vertex, device_vertex)
        _spinnaker.add_edge(edge)

    def create_munich_motor_population(
            self, spinnaker_link_id, speed=30, sample_time=4096,
            update_time=512, delay_time=5, delta_threshold=23,
            continue_if_not_different=True, model=IF_curr_exp, params=None):
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

        :param spinnaker_link_id: the spinnaker link to tie into
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
        spynnaker = get_spynnaker()
        population = Population(6, model, params, spynnaker,
                                "Robot Input Population")
        motor_control = MunichMotorControl(
            spynnaker.machine_time_step, spynnaker.timescale_factor,
            spinnaker_link_id, speed, sample_time, update_time, delay_time,
            delta_threshold, continue_if_not_different, "Robot Motor Control")
        spynnaker.add_vertex(motor_control)
        edge = MultiCastPartitionableEdge(
            population._get_vertex, motor_control, label="Robot input edge")
        spynnaker.add_edge(edge)
        return population
