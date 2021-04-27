import random as r
import numpy as np
from numba import njit
import pickle

import time

from ant import Ant
import conf as c

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import engine as e

update_time = 0

def update(dt=0):
    global update_time
    t0 = time.time()
    u = e.update(dt)
    if u:
        print(u)
    server.send_ants(e.ant_posistions(), e.ant_radians())
    t = time.time()-t0
    if t>update_time:
        update_time=t
        #print(update_time)


#def main():
#    e.load()
#    clock.schedule_interval(e.add_ants, 1/c.spawns_ps)
#    clock.schedule_interval(update, 1/c.pos_updates_ps)
#    clock.schedule_interval(e.switch_attractors, 1/c.attractor_tele_ps)
#    run()

def main():
    e.load()
    
    t=time.time()
    while True:
        current_time=time.time()
        if current_time-t>=1/c.pos_updates_ps:
            t=current_time
            update()
    

class MulticastServer(DatagramProtocol):
    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup("228.0.0.5")

        main()

    def datagramReceived(self, datagram, address):
        print("Datagram {} received from {}".format(repr(datagram), repr(address)))
        if datagram == b"Client: Ping" or datagram == "Client: Ping":
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            self.transport.write(b"Server: Pong", address)


    def send_ants(self, ant_pos, ant_rad):
        if ant_pos is not None and ant_rad is not None:
            out=pickle.dumps(np.column_stack((ant_pos, ant_rad)))
            self.transport.write(out, ("228.0.0.5", 9999))


server = MulticastServer()
reactor.listenMulticast(9999, server, listenMultiple=True)
reactor.run()
