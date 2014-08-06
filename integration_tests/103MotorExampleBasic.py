__author__ = 'stokesa6'
"""
motor example that just feeds data to the motor pop which starts the motor going forward
"""

#!/usr/bin/python
import spynnaker_with_external_devices.pyNN as p
import numpy, pylab

#set up pacman103
p.setup(timestep=1.0, min_delay = 1.0, max_delay = 32.0)

#external stuff population requiremenets
connected_chip_coords = {'x': 0, 'y': 0}
virtual_chip_coords = {'x': 0, 'y': 5}
link = 4

populations = list()
projections = list()


populations.append(p.Population(1, p.SpikeSourcePoisson, {'rate': 10000}))

populations.append(p.Population(1, p.MunichMotorControl,
                   {'virtual_chip_coords': virtual_chip_coords,
                    'connected_chip_coords':connected_chip_coords,
                    'connected_chip_edge':link},
                   label='External motor control'))

projections.append(p.Projection(populations[0], populations[1],
                   p.OneToOneConnector()))

p.run(10000)