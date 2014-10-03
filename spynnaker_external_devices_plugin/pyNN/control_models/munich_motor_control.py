from spinn_machine.processor import Processor
from spynnaker.pyNN.models.abstract_models.abstract_population_vertex import \
    AbstractPopulationVertex
from spynnaker_external_devices_plugin.pyNN.external_devices_models.\
    munich_motor_device import MunichMotorDevice
from spynnaker.pyNN.utilities import packet_conversions
from spynnaker.pyNN.utilities import constants
from spynnaker.pyNN.utilities.conf import config
from pacman.model.resources.cpu_cycles_per_tick_resource import \
    CPUCyclesPerTickResource

from pacman.model.constraints.vertex_has_dependent_constraint import \
    VertexHasDependentConstraint
from pacman.model.resources.dtcm_resource import DTCMResource
from pacman.model.resources.sdram_resource import SDRAMResource
from pacman.model.constraints.partitioner_maximum_size_constraint \
    import PartitionerMaximumSizeConstraint


from data_specification.data_specification_generator import \
    DataSpecificationGenerator

import os


class MunichMotorControl(AbstractPopulationVertex):

    SYSTEM_REGION = 0
    PARAMS_REGION = 1

    SYSTEM_SIZE = 16
    PARAMS_SIZE = 7 * 4
    _N_ATOMS = 6

    CORE_APP_IDENTIFIER = constants.MUNICH_MOTOR_CONTROL_CORE_APPLICATION_ID

    def __init__(self, n_neurons, virtual_chip_coords, connected_chip_coords,
                 connected_chip_edge, machine_time_step, speed=30,
                 sample_time=4096, update_time=512, delay_time=5,
                 delta_threshold=23, continue_if_not_different=True,
                 label="RobotMotorControl"):
        """
        constructor that depends upon the Component vertex
        """
        AbstractPopulationVertex.__init__(
            self, binary="robot_motor_control.aplx", label=label, n_neurons=6,
            max_atoms_per_core=6, n_params=3,
            machine_time_step=machine_time_step)

        max_constraint = \
            PartitionerMaximumSizeConstraint(MunichMotorControl._N_ATOMS)
        self.add_constraint(max_constraint)

        dependant_vertex_constraint =\
            VertexHasDependentConstraint(
                MunichMotorDevice(1, virtual_chip_coords,
                                  connected_chip_coords,
                                  connected_chip_edge, machine_time_step))
        self.add_constraint(dependant_vertex_constraint)

        self._binary = "robot_motor_control.aplx"

        self.virtual_chip_coords = virtual_chip_coords
        self.connected_chip_coords = connected_chip_coords
        self.connected_chip_edge = connected_chip_edge
        self.out_going_edge = None

        self.speed = speed
        self.sample_time = sample_time
        self.update_time = update_time
        self.delay_time = delay_time
        self.delta_threshold = delta_threshold
        self.continue_if_not_different = continue_if_not_different

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
        self._write_basic_setup_info(spec,
                                     MunichMotorControl.CORE_APP_IDENTIFER)

        spec.comment("\n*** Spec for robot motor control ***\n\n")

        #reserve regions
        self.reserve_memory_regions(spec)
        
        #write system info
        spec.switch_write_focus(region=self.SYSTEM_REGION)
        spec.write_value(data=0xBEEF0000)
        spec.write_value(data=0)
        spec.write_value(data=0)
        spec.write_value(data=0)
        edge_key = None
        #locate correct subedge for key
        for subedge in subvertex.out_subedges:
            if subedge.edge == self.out_going_edge:
                edge_key = subedge.key

        #write params to memory
        spec.switch_write_focus(region=self.PARAMS_REGION)
        spec.write_value(data=edge_key)
        spec.write_value(data=self.speed)
        spec.write_value(data=self.sample_time)
        spec.write_value(data=self.update_time)
        spec.write_value(data=self.delay_time)
        spec.write_value(data=self.delta_threshold)
        if self.continue_if_not_different:
            spec.write_value(data=1)
        else:
            spec.write_value(data=0)

        # End-of-Spec:
        spec.end_specification()
        data_writer.close()

    #inhirrited from data specable vertex
    @staticmethod
    def get_binary_file_name():
        common_binary_path = os.path.join(config.get("SpecGeneration",
                                                     "common_binary_folder"))

        binary_name = os.path.join(common_binary_path,
                                   'robot_motor_control.aplx')

        return binary_name

    def reserve_memory_regions(self, spec):
        """
        Reserve SDRAM space for memory areas:
        1) Area for information on what data to record
        2) area for start commands
        3) area for end commands
        """
        spec.comment("\nReserving memory space for data regions:\n\n")

        # Reserve memory:
        spec.reserveMemRegion(region=self.SYSTEM_REGION,
                              size=self.SYSTEM_SIZE,
                              label='setup')
        
        spec.reserveMemRegion(region=self.PARAMS_REGION,
                              size=self.PARAMS_SIZE,
                              label='params')

    @property
    def model_name(self):
        return "Munich Motor Control"

    def get_resources_used_by_atoms(self, vertex_slice, graph):
        resources = list()
        # noinspection PyTypeChecker
        resources.append(CPUCyclesPerTickResource(0))
        resources.append(DTCMResource(0))
        resources.append(SDRAMResource(self.SYSTEM_SIZE + self.PARAMS_SIZE))
        return resources

    def generate_routing_info(self, subedge):
        """
        overload component method and returns virtual chip key for routing info
        """
        x, y, p = subedge.postsubvertex.placement.processor.get_coordinates()
        key = packet_conversions.get_key_from_coords(x, y, p)
        return key, 0xffff0000

    def get_parameters(self):
        raise NotImplementedError

    def get_cpu_usage_for_atoms(self, vertex_slice):
        return (vertex_slice.hi_atom - vertex_slice.lo_atom) * \
               (Processor.CPU_AVAILABLE / self._n_atoms)

    def get_n_synapse_type_bits(self):
        return 1

    def write_synapse_parameters(self, spec, subvertex):
        pass