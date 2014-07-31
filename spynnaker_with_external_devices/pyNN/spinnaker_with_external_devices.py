from spynnaker.pyNN.spinnaker import Spinnaker

import logging

logger = logging.getLogger(__name__)


class SpinnakerWithExternalDevices(Spinnaker):

    def __init__(self, host_name=None, timestep=None, min_delay=None,
                 max_delay=None, graph_label=None):
        Spinnaker.__init__(self, host_name=host_name, timestep=timestep,
                           min_delay=min_delay, max_delay=max_delay,
                           graph_label=graph_label)