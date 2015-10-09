"""
MunichMotorControl
"""

# externald evice imports
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_motor_device import MunichMotorDevice

# spynnaker improts
from spynnaker.pyNN.models.abstract_models\
    .abstract_vertex_with_dependent_vertices import \
    AbstractVertexWithEdgeToDependentVertices
from spynnaker.pyNN import exceptions

# pacman imports
from pacman.model.constraints.key_allocator_constraints\
    .key_allocator_fixed_mask_constraint \
    import KeyAllocatorFixedMaskConstraint
from spinn_front_end_common.utilities import constants
from pacman.model.partitionable_graph.abstract_partitionable_vertex \
    import AbstractPartitionableVertex

# front end common imports
from spinn_front_end_common.abstract_models.abstract_data_specable_vertex\
    import AbstractDataSpecableVertex
from spinn_front_end_common.abstract_models\
    .abstract_provides_outgoing_edge_constraints\
    import AbstractProvidesOutgoingEdgeConstraints

from data_specification.data_specification_generator import \
    DataSpecificationGenerator

# general imports
import logging

logger = logging.getLogger(__name__)


class MunichMotorControl(AbstractDataSpecableVertex,
                         AbstractPartitionableVertex,
                         AbstractVertexWithEdgeToDependentVertices,
                         AbstractProvidesOutgoingEdgeConstraints):
    """
    the control model for the moters of a ombibot
    """

    SYSTEM_REGION = 0
    PARAMS_REGION = 1

    SYSTEM_SIZE = 4 * 4
    PARAMS_SIZE = 7 * 4

    def __init__(
            self, machine_timestep, timescale_factor, spinnaker_link_id,
            speed=30, sample_time=4096, update_time=512, delay_time=5,
            delta_threshold=23, continue_if_not_different=True,
            label="RobotMotorControl"):
        """
        """

        AbstractDataSpecableVertex.__init__(self, machine_timestep,
                                            timescale_factor)
        AbstractPartitionableVertex.__init__(self, 6, label, 6, None)
        AbstractVertexWithEdgeToDependentVertices.__init__(
            self, [MunichMotorDevice(spinnaker_link_id)])
        AbstractProvidesOutgoingEdgeConstraints.__init__(self)

        self._speed = speed
        self._sample_time = sample_time
        self._update_time = update_time
        self._delay_time = delay_time
        self._delta_threshold = delta_threshold
        self._continue_if_not_different = continue_if_not_different

    def get_outgoing_edge_constraints(self, partitioned_edge, graph_mapper):
        """

        :param partitioned_edge:
        :param graph_mapper:
        :return:
        """
        # Any key to the device will work, as long as it doesn't set the
        # management bit.  We also need enough for the configuration bits
        # and the management bit anyway
        return list([KeyAllocatorFixedMaskConstraint(0xFFFFF800)])

    def generate_data_spec(self, subvertex, placement, subgraph, graph,
                           routing_info, hostname, graph_subgraph_mapper,
                           report_folder, ip_tags, reverse_ip_tags,
                           write_text_specs, application_run_time_folder):
        """
        Model-specific construction of the data blocks necessary to build a
        single external retina device.
        :param subvertex:
        :param placement:
        :param subgraph:
        :param graph:
        :param routing_info:
        :param hostname:
        :param graph_subgraph_mapper:
        :param report_folder:
        :param ip_tags:
        :param reverse_ip_tags:
        :param write_text_specs:
        :param application_run_time_folder:
        :return:
        """
        # Create new DataSpec for this processor:
        data_writer, report_writer = \
            self.get_data_spec_file_writers(
                placement.x, placement.y, placement.p, hostname, report_folder,
                write_text_specs, application_run_time_folder)

        spec = DataSpecificationGenerator(data_writer, report_writer)

        # reserve regions
        self.reserve_memory_regions(spec)

        # Write the setup region
        spec.comment("\n*** Spec for robot motor control ***\n\n")
        self._write_basic_setup_info(spec, self.SYSTEM_REGION)

        # locate correct subedge for key
        edge_key = None
        if len(graph.outgoing_edges_from_vertex(self)) != 1:
            raise exceptions.ConfigurationException(
                "This motor should only have one outgoing edge to the robot")

        for subedge in subgraph.outgoing_subedges_from_subvertex(subvertex):
            edge_keys_and_masks = \
                routing_info.get_keys_and_masks_from_subedge(subedge)
            edge_key = edge_keys_and_masks[0].key

        # write params to memory
        spec.switch_write_focus(region=self.PARAMS_REGION)
        spec.write_value(data=edge_key)
        spec.write_value(data=self._speed)
        spec.write_value(data=self._sample_time)
        spec.write_value(data=self._update_time)
        spec.write_value(data=self._delay_time)
        spec.write_value(data=self._delta_threshold)
        if self._continue_if_not_different:
            spec.write_value(data=1)
        else:
            spec.write_value(data=0)

        # End-of-Spec:
        spec.end_specification()
        data_writer.close()

    # inherited from data specable vertex
    def get_binary_file_name(self):
        """
        string containing name of this vertex c binary
        :return:
        """
        return "robot_motor_control.aplx"

    def reserve_memory_regions(self, spec):
        """
        Reserve SDRAM space for memory areas:
        1) Area for information on what data to record
        2) area for start commands
        3) area for end commands
        :param spec: the databspec object
        """
        spec.comment("\nReserving memory space for data regions:\n\n")

        # Reserve memory:
        spec.reserve_memory_region(
            region=self.SYSTEM_REGION,
            size=constants.DATA_SPECABLE_BASIC_SETUP_INFO_N_WORDS * 4,
            label='setup')

        spec.reserve_memory_region(region=self.PARAMS_REGION,
                                   size=self.PARAMS_SIZE,
                                   label='params')

    @property
    def model_name(self):
        """
        human readable name of this vertex
        :return:
        """
        return "Munich Motor Control"

    def get_sdram_usage_for_atoms(self, vertex_slice, graph):
        """
        returns the sdram usage of this vertex
        :param vertex_slice:
        :param graph:
        :return:
        """
        return self.SYSTEM_SIZE + self.PARAMS_SIZE

    def get_dtcm_usage_for_atoms(self, vertex_slice, graph):
        """
        returns the amount of dtcm used by this vertex
        :param vertex_slice:
        :param graph:
        :return:
        """
        return 0

    def get_cpu_usage_for_atoms(self, vertex_slice, graph):
        """
        helper method for parittioning.
        :param vertex_slice:
        :param graph:
        :return:
        """
        return 0

    def has_dependent_vertices(self):
        """
        helper method for is instance
        :return:
        """
        return True

    def is_data_specable(self):
        """
        helper method for is instance
        :return:
        """
        return True

    def partition_identifer_for_dependent_edge(self, dependent_edge):
        """ helper emthod for the vertex to give semantic data of the partition
        uidentifer type for each depdent vertex.

        :param dependent_edge: the edge which coems from this to one of its
        dependent vertices.
        :return: the outgoing spike parittion identifer for this depdentent edge
        """
        if isinstance(dependent_edge.post_vertex, MunichMotorDevice):
            return "motor commands"
        else:
            raise exceptions.ConfigurationException(
                "I have a edge whose destination i dont recongise {}->{} ( I "
                "only reconginse edges to my dependent vertex of a "
                "MunichMotorDevice. please fix and try again"
                .format(self, dependent_edge.post_vertex))
