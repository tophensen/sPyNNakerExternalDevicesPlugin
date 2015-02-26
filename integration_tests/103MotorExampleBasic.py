"""
motor example that just feeds data to the motor pop which starts the motor going forward
"""

#!/usr/bin/python
import spynnaker.pyNN as p
import spynnaker_external_devices_plugin.pyNN as q

#set up pacman103
p.setup(timestep=1.0, min_delay=1.0, max_delay=32.0)

#external stuff population requiremenets
connected_chip_coords = {'x': 0, 'y': 0}
virtual_chip_coords = {'x': 0, 'y': 5}
link = 4

populations = list()
projections = list()


populations.append(p.Population(1, p.SpikeSourcePoisson, {'rate': 10000}))

populations.append(p.Population(1, q.MunichMotorControl,
                   {'virtual_chip_x': 0,
                    'virtual_chip_y': 5,
                    'connected_to_real_chip_x': 0,
                    'connected_to_real_chip_y': 0,
                    'connected_chip_edge': link},
                   label='External motor control'))

projections.append(p.Projection(populations[0], populations[1],
                   p.FromListConnector([(0, 1, 1, 1)])))

p.run(10000)