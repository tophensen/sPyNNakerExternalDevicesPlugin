import spynnaker.pyNN as frontend
import spynnaker_external_devices_plugin.pyNN as externaldevices
import pylab

from spynnaker.pyNN.utilities.database.socket_address import SocketAddress
socket_addresses = list()
socket_addresses.append(SocketAddress(
    listen_port=19998, notify_port_no=19999, notify_host_name="localhost"))
socket_addresses.append(SocketAddress(
    listen_port=19997, notify_port_no=19996, notify_host_name="localhost"))

frontend.setup(timestep=1.0, min_delay=1.0, max_delay=144.0,
               database_socket_addresses=socket_addresses)

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

cell_params_spike_injector = {'port': 12345}

populations = list()
projections = list()

weight_to_spike = 2.0

populations.append(frontend.Population(nNeurons, frontend.IF_curr_exp,
                                       cell_params_lif, label='pop_1'))
populations.append(
    frontend.Population(nNeurons, externaldevices.SpikeInjector,
                        cell_params_spike_injector,
                        label='spike_injector_1'))

populations[0].record()
externaldevices.activate_live_output_for(populations[0])

projections.append(frontend.Projection(
    populations[1], populations[0],
    frontend.OneToOneConnector(weights=weight_to_spike)))

connections = list()
for i in range(0, nNeurons - 1):
    singleConnection = (i, ((i + 1) % nNeurons), weight_to_spike, 3)
    connections.append(singleConnection)

projections.append(frontend.Projection(populations[0], populations[0],
                   frontend.FromListConnector(connections)))


frontend.run(run_time)

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

frontend.end()