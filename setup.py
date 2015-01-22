from setuptools import setup

setup(
    name="sPyNNakerExternalDevicesPlugin",
    version="2015.007",
    description="Spinnaker External Devices Plugin",
    url="https://github.com/SpiNNakerManchester/SpyNNaker",
    packages=['spynnaker_external_devices_plugin',
              'spynnaker_external_devices_plugin.pyNN',
              'spynnaker_external_devices_plugin.pyNN.abstract_models',
              'spynnaker_external_devices_plugin.pyNN.control_models',
              'spynnaker_external_devices_plugin.pyNN.external_devices_models',
              'spynnaker_external_devices_plugin.pyNN.interfaces',
              'spynnaker_external_devices_plugin.pyNN.links'],
    install_requires=['sPyNNaker >= 2015.003']
)
