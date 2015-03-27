#!/usr/bin/python
from pyNN.spiNNaker import *
import spynnaker_external_devices_plugin.pyNN as p
import numpy
import matplotlib.pyplot as p_plot

setup(timestep=1.0, min_delay = 1.0, max_delay = 8.0, db_name='synfire.sqlite')

n_pop = 2 #60
nNeurons = 10 #100

rng = NumpyRNG(seed=28374)
rng1 = NumpyRNG(seed=12345)

delay_distr = RandomDistribution('uniform', [5,10], rng)
weight_distr = RandomDistribution('uniform', [0,2], rng1)

v_distr = RandomDistribution('uniform', [-55,-95], rng)

v_inits = []
for i in range(nNeurons):
    v_inits.append(v_distr.next())

cell_params_lif_in = { 'tau_m'      : 32,
                'v_init'    : -80,
                'v_rest'     : -75,   
                'v_reset'    : -95,  
                'v_thresh'   : -55,
                'tau_syn_E'   : 5,
                'tau_syn_I'   : 10,
                'tau_refrac'   : 20, 
                'i_offset'   : 1
                }

cell_params_lif = { 'tau_m'      : 32,
                'v_init'    : -80,
                'v_rest'     : -75,   
                'v_reset'    : -95,  
                'v_thresh'   : -55,
                'tau_syn_E'   : 5,
                'tau_syn_I'   : 10,
                'tau_refrac'   : 5,                 
                'i_offset'   : 0 
                }

cell_params_ext_dev = {'host_port_number': 34567,
                'tag': 3,
                'virtual_key': 0
                }


populations = list()
projections = list()

weight_to_spike = 20

populations.append(Population(nNeurons, IF_curr_exp, cell_params_lif_in, label='pop_%d' % 0))
populations[0].randomInit(v_distr)

p.activate_live_output_for(populations[0], port=34567, host="130.88.198.209", tag=2, payload_as_time_stamps=False, use_payload_prefix=False)
#populations.append(Population(nNeurons, IF_curr_exp, cell_params_lif, label='pop_%d' % i))

pop_external = Population(nNeurons, p.ReverseIpTagMultiCastSource, cell_params_ext_dev, label='Babel_Dummy')

populations.append(Population(nNeurons, IF_curr_exp, cell_params_lif, label='pop_%d' % 1))

projections.append(Projection(pop_external, populations[1], OneToOneConnector(weights=weight_to_spike, delays=10)))

#populations[0].record_v()           # at the moment is only possible to observe one population per core
populations[1].record_v()

for pop in populations:        
    pop.record(to_file=False) # sends spike to the Monitoring application

#    populations[i].record_variable('rate', save_to='eth') # sends spike to the Monitoring application
    
run(10000)

# retrieving spike results and plotting...

id_accumulator=0

for pop_o in populations:
    data = numpy.asarray(pop_o.getSpikes())
    p_plot.scatter(data[:,0], data[:,1] + id_accumulator, color='green', s=1)
    id_accumulator = id_accumulator + pop_o.size

p_plot.show()



