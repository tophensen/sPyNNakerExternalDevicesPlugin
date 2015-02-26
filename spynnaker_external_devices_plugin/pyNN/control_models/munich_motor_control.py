from pacman.model.resources.resource_container import ResourceContainer
from spinn_machine.processor import Processor


from spynnaker.pyNN.models.abstract_models.abstract_population_vertex import \
    AbstractPopulationVertex
from spynnaker.pyNN.models.abstract_models.abstract_provides_fixed_mask_vertex\
    import AbstractProvidesFixedMaskVertex
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_motor_device import MunichMotorDevice
from spynnaker.pyNN.utilities import constants
from spynnaker.pyNN.models.abstract_models\
    .abstract_vertex_with_dependent_vertices import \
    AbstractVertexWithEdgeToDependentVertices
from spynnaker.pyNN import exceptions


from pacman.model.resources.cpu_cycles_per_tick_resource import \
    CPUCyclesPerTickResource
from pacman.model.resources.dtcm_resource import DTCMResource
from pacman.model.resources.sdram_resource import SDRAMResource
from pacman.model.constraints.partitioner_maximum_size_constraint \
    import PartitionerMaximumSizeConstraint


from data_specification.data_specification_generator import \
    DataSpecificationGenerator

import logging


logger = logging.getLogger(__name__)


class MunichMotorControl(AbstractPopulationVertex,
                         AbstractProvidesFixedMaskVertex,
                         AbstractVertexWithEdgeToDependentVertices):

    SYSTEM_REGION = 0
    PARAMS_REGION = 1

    SYSTEM_SIZE = 10 * 4
    PARAMS_SIZE = 15 * 4
    _N_ATOMS = 6

    CORE_APP_IDENTIFIER = constants.MUNICH_MOTOR_CONTROL_CORE_APPLICATION_ID
    _model_based_max_atoms_per_core = 6

    def __init__(self, n_neurons, spikes_per_second, ring_buffer_sigma,
                 timescale_factor, virtual_chip_x, virtual_chip_y,
                 connected_to_real_chip_x, connected_to_real_chip_y,
                 connected_chip_edge, machine_time_step, speed=30,
                 sample_time=4096, update_time=512, delay_time=5,
                 delta_threshold=23, continue_if_not_different=True,
                 label="RobotMotorControl"):
        """
        constructor that depends upon the Component vertex
        """
        if n_neurons != 6:
            logger.warning(
                "The Munich Motor control will have exactly 6 neurons!")

        AbstractPopulationVertex.__init__(
            self, binary="robot_motor_control.aplx", label=label, n_neurons=6,
            max_atoms_per_core=(MunichMotorControl
                                ._model_based_max_atoms_per_core),
            n_params=3, spikes_per_second=spikes_per_second,
            ring_buffer_sigma=ring_buffer_sigma,
            machine_time_step=machine_time_step,
            timescale_factor=timescale_factor)
        AbstractProvidesFixedMaskVertex.__init__(self)

        dependent_vertices = list()
        dependent_vertices.append(
            MunichMotorDevice(
                1, virtual_chip_x, virtual_chip_y,
                connected_to_real_chip_x, connected_to_real_chip_y,
                connected_chip_edge, machine_time_step, timescale_factor,
                ring_buffer_sigma, spikes_per_second))

        AbstractVertexWithEdgeToDependentVertices.__init__(self,
                                                           dependent_vertices)

        max_constraint = \
            PartitionerMaximumSizeConstraint(MunichMotorControl._N_ATOMS)
        self.add_constraint(max_constraint)

        self._speed = speed
        self._sample_time = sample_time
        self._update_time = update_time
        self._delay_time = delay_time
        self._delta_threshold = delta_threshold
        self._continue_if_not_different = continue_if_not_different

    def get_fixed_mask_for_partitioned_edge(self, partitioned_edge,
                                            graph_mapper):

        # The only edge out of this vertex should be the one to the
        # robot motor itself
        return 0xFFFFF800

    @staticmethod
    def set_model_max_atoms_per_core(new_value):
        MunichMotorControl._model_based_max_atoms_per_core = new_value

    def generate_data_spec(self, subvertex, placement, subgraph, graph,
                           routing_info, hostname, graph_subgraph_mapper,
                           report_folder):
        """
        Model-specific construction of the data blocks necessary to build a
        single external retina device.
        """
        # Create new DataSpec for this processor:
        data_writer, report_writer = \
            self.get_data_spec_file_writers(
                placement.x, placement.y, placement.p, hostname, report_folder)

        spec = DataSpecificationGenerator(data_writer, report_writer)

        # reserve regions
        self.reserve_memory_regions(spec)

        self._write_basic_setup_info(spec, self.CORE_APP_IDENTIFIER)

        spec.comment("\n*** Spec for robot motor control ***\n\n")

        # write system info
        spec.switch_write_focus(region=self.SYSTEM_REGION)
        spec.write_value(data=0xBEEF0000)
        spec.write_value(data=0)
        spec.write_value(data=0)
        spec.write_value(data=0)
        edge_key = None

        # locate correct subedge for key
        if len(graph.outgoing_edges_from_vertex(self)) > 1:
            raise exceptions.ConfigurationException(
                "The motor vertex has more than one edge going to it. This is "
                "deemed an error from the point of view of this model. Please"
                " either build a new model, extend this one, or rectify your"
                " script and try again.")

        for subedge in subgraph.outgoing_subedges_from_subvertex(subvertex):
            edge_keys_and_masks = \
                routing_info.get_keys_and_masks_from_subedge(subedge)
            edge_key = edge_keys_and_masks[0].key

        # write params to memory
        spec.switch_write_focus(region=self.PARAMS_REGION)
        if edge_key is None:
            spec.write_value(data=0)
            spec.write_value(data=0)
        else:
            spec.write_value(data=1)
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
        return "robot_motor_control.aplx"

    def reserve_memory_regions(self, spec):
        """
        Reserve SDRAM space for memory areas:
        1) Area for information on what data to record
        2) area for start commands
        3) area for end commands
        """
        spec.comment("\nReserving memory space for data regions:\n\n")

        # Reserve memory:
        spec.reserve_memory_region(region=self.SYSTEM_REGION,
                                   size=self.SYSTEM_SIZE,
                                   label='setup')

        spec.reserve_memory_region(region=self.PARAMS_REGION,
                                   size=self.PARAMS_SIZE,
                                   label='params')

    @property
    def model_name(self):
        return "Munich Motor Control"

    def get_resources_used_by_atoms(self, vertex_slice, graph):
        resources = ResourceContainer(
            cpu=CPUCyclesPerTickResource(0), dtcm=DTCMResource(0),
            sdram=SDRAMResource(self.SYSTEM_SIZE + self.PARAMS_SIZE))
        return resources

    def get_parameters(self):
        raise NotImplementedError

    def get_cpu_usage_for_atoms(self, vertex_slice, graph):
        return (vertex_slice.hi_atom - vertex_slice.lo_atom) * \
               (Processor.CPU_AVAILABLE / self._n_atoms)

    def get_n_synapse_type_bits(self):
        return 1

    def write_synapse_parameters(self, spec, subvertex, vertex_slice):
        pass

    def is_population_vertex(self):
        return True

    def is_recordable(self):
        return True

    def has_dependent_vertices(self):
        return True