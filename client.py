from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from threading import Thread

import numpy as np
import pickle

#import conf as c
from queue import Queue

import ui

rec_packets = Queue()
        
class MulticastClient(DatagramProtocol):
    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup("228.0.0.5")

    def datagramReceived(self, datagram, address):
        packet=pickle.loads(datagram)
        rec_packets.put(packet)

     
def consume_packet(dx):
    #print(rec_packets.qsize())
    if rec_packets.qsize()>1:
        print(f'Client skipped {rec_packets.qsize()-1} packet(s).')
        for _ in range(rec_packets.qsize()-1):
            rec_packets.get()
    if not rec_packets.empty():
        packet=rec_packets.get()
        packet*=ui.scale_factor #scale positions as well as radians 
        packet[:,:2]+=ui.coords_origin
        for i,p in enumerate(packet):
            ant_pos,ant_rad = p[:2],p[2]
            ui.circles[i].position=tuple(ant_pos)
            ui.circles[i].radius=float(ant_rad)
        for i in range(len(packet),ui.circle_count):
            ui.circles[i].position=(-1000,-1000)
            ui.circles[i].radius=0.


reactor.listenMulticast(9999, MulticastClient(), listenMultiple=True)
Thread(target=reactor.run,
        kwargs={"installSignalHandlers": False}, 
        ).start()

ui.schedule_interval(consume_packet, 10**-3)
ui.run()
