import spynnaker.pyNN as p
import spynnaker_external_devices_plugin.pyNN as q

p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)

nNeurons = 100
run_time = 560

cell_params_lif = {'cm'        : 0.25, # nF
                   'i_offset'  : 0.0,
                   'tau_m'     : 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E' : 5.0,
                   'tau_syn_I' : 5.0,
                   'v_reset'   : -70.0,
                   'v_rest'    : -65.0,
                   'v_thresh'  : -50.0
                  }

cell_params_spike_injector = {'host_port_number' : 19876,
                              'host_ip_address'  : 123,
                              'virtual_key'      : 458752,
                              'prefix'           : None,
                              'prefix_type'      : None}

populations = list()
projections = list()

weight_to_spike = 2.0

populations.append(p.Population(nNeurons, p.IF_curr_exp,
                                cell_params_lif, label='pop_1'))
populations.append(p.Population(nNeurons, q.SpikeInjector,
                                cell_params_spike_injector,
                                label='spike_injector_1'))

projections.append(p.Projection(populations[1], populations[0],
                                p.AllToAllConnector()))


p.run(run_time)
p.end()