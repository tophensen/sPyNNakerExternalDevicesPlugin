"""
The :py:mod:`spynnaker.pynn` package contains the frontend specifications
and implementation for the PyNN High-level API
(http://neuralensemble.org/trac/PyNN)
"""

#external models
from spynnaker_with_external_devices.pyNN.external_devices_models.\
    external_cochlea_device import ExternalCochleaDevice
from spynnaker_with_external_devices.pyNN.external_devices_models.\
    external_fpga_retina_device import ExternalFPGARetinaDevice
from spynnaker_with_external_devices.pyNN.external_devices_models.\
    munich_motor_device import MunichMotorDevice
from spynnaker_with_external_devices.pyNN.external_devices_models.\
    munich_retina_device import MunichRetinaDevice
from spynnaker_with_external_devices.pyNN.control_models.munich_motor_control \
    import MunichMotorControl