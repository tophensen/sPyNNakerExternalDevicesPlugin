__author__ = 'stokesa6'
"""
retina example that just feeds data from retina to vis
"""

#!/usr/bin/python
import spynnaker_with_external_devices.pyNN as p
import visualiser.visualiser_constants as modes
import numpy, pylab
import retina_lib as retina_lib

#set up pacman103
p.setup(timestep=1.0, min_delay = 1.0, max_delay = 32.0)

p.set_number_of_neurons_per_core('IF_curr_exp', 128)      # this will set one population per core

cell_params_lif = {'cm'        : 0.25, # nF
                     'i_offset'  : 0.0,
                     'tau_m'     : 10.0,
                     'tau_refrac': 2.0,
                     'tau_syn_E' : 0.5,
                     'tau_syn_I' : 0.5,
                     'v_reset'   : -65.0,
                     'v_rest'    : -65.0,
                     'v_thresh'  : -64.4 #wow... this is really close
                     }

#external stuff population requiremenets
connected_chip_coords = {'x': 0, 'y': 0}
virtual_chip_coords = {'x': 0, 'y': 5}
link = 4
#link = 3

populations = list()
projections = list()

populations.append(p.Population(1, p.MunichRetinaDevice,
                   {'virtual_chip_coords': virtual_chip_coords,
                    'connected_chip_coords':connected_chip_coords,
                    'connected_chip_edge':link,
                    'polarity':p.MunichRetinaDevice.DOWN_POLARITY,
                    'position': p.MunichRetinaDevice.RIGHT_RETINA},
                   label='External retina'))

populations.append(p.Population(1, p.MunichRetinaDevice,
                   {'virtual_chip_coords': virtual_chip_coords,
                    'connected_chip_coords':connected_chip_coords,
                    'connected_chip_edge':link,
                    'polarity':p.MunichRetinaDevice.UP_POLARITY,
                    'position': p.MunichRetinaDevice.RIGHT_RETINA},
                   label='External retina'))

'''
populations.append(p.Population(1, p.MunichRetinaDevice,
                  {'virtual_chip_coords': virtual_chip_coords,
                    'connected_chip_coords':connected_chip_coords,
                    'connected_chip_edge':link,
                    'unique_id': 'L'},
                   label='External retina'))


populations.append(p.Population(16*16, p.ExternalFPGARetinaDevice,
                   {'virtual_chip_coords': virtual_chip_coords,
                    'connected_chip_coords':connected_chip_coords,
                    'connected_chip_edge':link},
                   label='External retina'))


populations.append(p.Population(p.ExternalFPGARetinaDevice.MODE_128,
                                p.ExternalFPGARetinaDevice,
                                {'virtual_chip_coords': virtual_chip_coords,
                                 'connected_chip_coords': connected_chip_coords,
                                 'connected_chip_edge': link,
                                 'polarity': p.ExternalFPGARetinaDevice.UP_POLARITY},
                                label='External retina'))

populations.append(p.Population(p.ExternalFPGARetinaDevice.MODE_128,
                                p.ExternalFPGARetinaDevice,
                   {'virtual_chip_coords': virtual_chip_coords,
                    'connected_chip_coords': connected_chip_coords,
                    'connected_chip_edge': link,
                    'polarity': p.ExternalFPGARetinaDevice.DOWN_POLARITY},
                   label='External retina'))
'''

#loopConnections = list()
#for i in range(0, 1):
#    singleConnection = (i, ((i + 1) % 1), 1, 1)
#    loopConnections.append(singleConnection)

populations.append(p.Population(1024, p.IF_curr_exp, cell_params_lif, label='pop_1'))
projections.append(p.Projection(populations[0], populations[2], p.FromListConnector(retina_lib.subSamplerConnector2D(128,32,.2,1))))
projections.append(p.Projection(populations[1], populations[2], p.FromListConnector(retina_lib.subSamplerConnector2D(128,32,.2,1))))

populations[0].record(visualiser_mode=modes.TOPOLOGICAL, visualiser_2d_dimension={'x':128, 'y':128})
populations[1].record(visualiser_mode=modes.TOPOLOGICAL, visualiser_2d_dimension={'x':128, 'y':128})
#populations[1].record()
p.run(100000)