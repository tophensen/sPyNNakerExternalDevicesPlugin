from pacman.model.abstract_classes.abstract_virtual_vertex \
    import AbstractVirtualVertex


class MunichMotorDevice(AbstractVirtualVertex):

    def __init__(self, spinnaker_link_id):

        AbstractVirtualVertex.__init__(
            self, 6, spinnaker_link_id,
            "External Munich Motor", max_atoms_per_core=6)

    @property
    def model_name(self):
        return "external motor device"

    def is_virtual_vertex(self):
        return True
