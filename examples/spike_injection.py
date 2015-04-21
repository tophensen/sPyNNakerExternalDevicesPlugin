import spynnaker.pyNN as FrontEnd
import spynnaker_external_devices_plugin.pyNN as ExternalDevices

import pylab

FrontEnd.setup(timestep=1.0)

nNeurons = 100
run_time = 10000

cell_params_lif = {'cm'        : 0.25,  # nF
                   'i_offset'  : 0.0,
                   'tau_m'     : 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E' : 5.0,
                   'tau_syn_I' : 5.0,
                   'v_reset'   : -70.0,
                   'v_rest'    : -65.0,
                   'v_thresh'  : -50.0
                   }

cell_params_spike_injector_new = {
    'virtual_key':      0x70800,
    'port':             12345}

populations = list()
projections = list()

weight_to_spike = 2.0

populations.append(FrontEnd.Population(nNeurons, FrontEnd.IF_curr_exp,
                                       cell_params_lif, label='pop_1'))
populations.append(
    FrontEnd.Population(
        nNeurons, ExternalDevices.SpikeInjector,
        cell_params_spike_injector_new, label='spike_injector_1'))

populations[0].record()
ExternalDevices.activate_live_output_for(populations[0])

projections.append(
    FrontEnd.Projection(
        populations[1], populations[0],
        FrontEnd.OneToOneConnector(weights=weight_to_spike)))

loopConnections = list()
for i in range(0, nNeurons - 1):
    singleConnection = (i, ((i + 1) % nNeurons), weight_to_spike, 3)
    loopConnections.append(singleConnection)

projections.append(FrontEnd.Projection(populations[0], populations[0],
                   FrontEnd.FromListConnector(loopConnections)))


FrontEnd.run(run_time)

spikes = populations[0].getSpikes(compatible_output=True)

if spikes is not None:
    print spikes
    pylab.figure()
    pylab.plot([i[1] for i in spikes], [i[0] for i in spikes], ".")
    pylab.ylabel('neuron id')
    pylab.xlabel('Time/ms')
    pylab.title('spikes')
    pylab.show()
else:
    print "No spikes received"

FrontEnd.end()