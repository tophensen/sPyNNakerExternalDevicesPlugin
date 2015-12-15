"""
io example that connects an IO board as virtual chip to a spike source 
in order to remote control it. 
The example needs remote spike sources as implemented by Christoph Richter/NST
c.richter@tum.de
It obviously needs an NST IO-board plugged into SpiNNaker, 
as well as a USB-serial interface to it.
pyserial is used to talk to the interface, 
the actual packets are sent using threading.Timer, 
timer threads are given to p.run() and executed just before 
the SpiNNaker cores are started. 
(requires a straightforward modification of sPynnaker)
"""
#import IPython
from pylab import *
import spynnaker.pyNN as p
from spynnaker.pyNN.utilities.multi_cast_command import MultiCastCommand
import spynnaker_external_devices_plugin.pyNN as q
from spinn_front_end_common.utilities.connections.live_event_connection \
    import LiveEventConnection

import serial
import time
from random import shuffle
from threading import Timer

sio = serial.Serial('/dev/ttyUSB0',4000000,rtscts=True,timeout=1)

# to track when we actually sent the commands
actual_sendtimes = []
def send_str_to_io(t):
    sio.write(t)
    actual_sendtimes.append(time.time())
    
def send_mcpl_packet(key,payload):
    c = "@" + key + '.' + payload + '\n'
    sio.write(c)
    print c    
#sio.write("E0\n")


duration=20000
# set up the tools
p.setup(timestep=1.0, min_delay=1.0, max_delay=32.0)

# link to IO-board
link = 1

populations = list()
projections = list()

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0,
                   'e_rev_E': 0.,
                   'e_rev_I': -80.
                   }
nn=128

# for some reason our pops have to project somewhere. 
nonpop = p.Population(nn, p.IF_cond_exp, cell_params_lif)

# minimum and maximum value the remote control channel should react to 
# sensor values are conveyed via payload 
sensor_min,sensor_max = 0, 20000
# minimum and maximum rate (Hz) at which a single neuron is supposed to fire
# note that min rate is actually bounded to 1/(32767 * machine_timestep)~0.03Hz
rate_min,rate_max = 0.1, 100.
# half width of RBF-neuron receiptive fields in neuron units 
# i.e. 1 is the distance between consecutive preferred values
gauss_width = 1.5 

input_pops=[]
remote_pops=[]
projections=[]

for i,source_type in enumerate([p.SpikeSourceDeterministicRate, 
                                p.SpikeSourceDeterministicRBF,
                                p.SpikeSourcePoissonRate,
                                p.SpikeSourcePoissonRBF]):
    input_population = p.Population(nn, source_type, 
                                    {'rate': rate_min, 
                                     'sensor_min' : sensor_min,
                                     'sensor_max' : sensor_max,
                                     'min_rate': rate_min,
                                     'max_rate': rate_max,
                                     'gauss_width': gauss_width},
                                     label="remote%i"%i)                                 
    input_population.record()
    # project to our dummy pop
    projections.append(p.Projection(input_population, nonpop, p.OneToOneConnector(weights=0.2,delays=1.0)))
    input_pops.append(input_population)

    # this is the remote control
    # key and mask refer to the remote control channel. 
    # Send your remote commands/sensor values with this key.
    io_population = q.MunichIODeviceSource(
        spinnaker_link_id=link,
        msg_key=0xFEFE0030 + i,msg_mask=0xFFFFFFFF)
    # we connect them this way
    q.spynnaker_external_devices.link_to_io_device_source(io_population,input_population)
    remote_pops.append(io_population)

# now let's set up a remote command sender via the serial port (ttyUSB)
actual_sendvalues=[]
mythreads=[]
offset=0.0
# how often do you want to update the value (tried and tested down to 1kHz)
period = 0.01	# in seconds, should work down to 0.002 or so, 
                # note this will create many threads and lots of IO 
starttime = time.time()
# define functions
sinf=lambda x: int((cos(4*2.*pi/(duration/1000.) *x))/2. * (sensor_max - sensor_min)*(x/(duration/1000.)) + (sensor_max-sensor_min)/2.)
stepf=lambda x: int(20*x/(duration/1000.+offset))* (sensor_max - sensor_min)/20 + sensor_min
popnums = [0,1,2,3]
# now set up commands and command senders as threading.Timer
for t in arange(offset, offset + duration/1000.,period):
    #shuffle order in which remotes are set
    shuffle(popnums)
    iostr = ""
    # prepare command string for all 4 spike sources
    for i in popnums:
       x = sinf(t)   
       payload = format(x,"08x")
       key = "FEFE003%i"%i
       # iostr is the string we send to the debug port of our IO board
       iostr = iostr + "@" + key + '.' + payload + '\n'
    # our commands are stored in actual_sendvalues
    print t,x
    actual_sendvalues.append(x)
    # append a threading.Timer to list of threads
    mythreads.append(Timer(t,send_str_to_io,args=[iostr]))


def start_threads(label,hook):
  """this starts the timed sender threads"""
  print "starting timer threads"
  for t in mythreads:
    t.start()

# this is a workaround to start the input-via-serial threads along with the simulation
injector_forward = p.Population(
    100, q.SpikeInjector,
    {'port':12346,'virtual_key':0x7000}, label='dummy_injector')
live = LiveEventConnection("LiveSpikeReceiver",send_labels=['dummy_injector'],local_port=19999,receive_labels=None)
live.add_start_callback("dummy_injector",start_threads)

p.run(duration)

# wait for serial senders to finish (just in case)
for t in mythreads:
  t.join()
  
# actual_sendtimes are when packets got actually sent
# but how do we align this with SpiNNaker's time?
# let's just assume first shot was at t=0...
actual_sendtimes = array(actual_sendtimes) - actual_sendtimes[0]

spike_fig = figure("spikes", figsize=(8,8))
rate_fig = figure("rates", figsize=(8,8))
for i,p in enumerate(input_pops):
    nn = p.size
    figure(spike_fig.number)
    subplot(2,2,i+1)
    poptyp = str(p._vertex)
    goidx = poptyp.rfind(".") + 1
    toidx = poptyp.find(" ",goidx)
    poptyp = poptyp[goidx:toidx]
    title(poptyp)
    s=transpose(p.getSpikes())
    s=sorted(zip(s[1],s[0]))
    s=transpose(s)
    spikesplot, = plot(array(s[0])/1000.,s[1],'s',alpha=0.1,ms=2.4)
    valuesplot, = plot(array(actual_sendtimes),1.*p.size*(array(actual_sendvalues)-p._vertex.sensor_min)/p._vertex.sensor_max,drawstyle='steps-post',lw=1.6)
    xlabel("time (s)")
    ylabel("#neuron, average rate (a.u.)")
    xlim(0,duration/1e3)
    ylim(0,p.size)

    figure(rate_fig.number)
    subplot(2,2,i+1)
    title(poptyp)
    windowsize = 0.08 * 1e3 # mseconds
    resolution = 0.02 * 1e3
    roughtime = []
    density = []
    ivon,ibis = 0,0
    tstart = 0.0
    while tstart < duration - windowsize:
        ivon = searchsorted(s[0],tstart,side='left')
        ibis = searchsorted(s[0],tstart+windowsize,side='right')
        roughtime.append((tstart+windowsize/2.)/1000.)
        density.append((ibis-ivon)/(windowsize/1e3)/nn)
        tstart += resolution
    mratesplot, = plot(roughtime,density,marker='o',mec='k',lw=0.5,ms=2.0)
    # get maximum spike rate
    rate_scale = p._vertex.max_rate
    offset = 0
    # if rbf-type, scale spike rate taking into account gauss_width
    if "rbf" in p._vertex.get_binary_file_name():
      # rough scaling to have the right OoM in the plot
      rate_scale = rate_scale / nn * sqrt(2) * gauss_width
      offset = rate_scale
     
    sratesplot, = plot(array(actual_sendtimes),offset + rate_scale*(array(actual_sendvalues)-p._vertex.sensor_min)/p._vertex.sensor_max,drawstyle='steps-post',lw=1.6)
    xlabel("time (s)")
    ylabel("average rate (Hz)")
    xlim(0,duration/1e3)
    ylim(0,offset + rate_scale)

figure(rate_fig.number)
subplots_adjust(0.09,0.08,0.97,0.94,0.3,0.4)
figlegend( (mratesplot, sratesplot), ('meas. rates', 'given rates'), 'center' ) 

figure(spike_fig.number)
subplots_adjust(0.09,0.08,0.97,0.94,0.3,0.4)
figlegend( (spikesplot, valuesplot), ('spikes', 'given rates'), 'center' )    
    
show()
