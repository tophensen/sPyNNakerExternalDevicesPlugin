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

    def create_munich_motor_population(
            self, virtual_chip_x, virtual_chip_y, connected_to_real_chip_x,
            connected_to_real_chip_y, connected_to_real_chip_link_id, speed=30,
            sample_time=4096, update_time=512, delay_time=5,
            delta_threshold=23, continue_if_not_different=True,
            model=IF_curr_exp, params={}):
        spynnaker = get_spynnaker()
        population = Population(6, model, params, spynnaker,
                                "Robot Input Population")
        motor_control = MunichMotorControl(
            spynnaker.machine_time_step, spynnaker.timescale_factor,
            virtual_chip_x, virtual_chip_y, connected_to_real_chip_x,
            connected_to_real_chip_y, connected_to_real_chip_link_id, speed,
            sample_time, update_time, delay_time, delta_threshold,
            continue_if_not_different, "Robot Motor Control")
        spynnaker.add_vertex(motor_control)
        edge = MultiCastPartitionableEdge(
            population._get_vertex, motor_control, label="Robot input edge")
        spynnaker.add_edge(edge)
        return population
