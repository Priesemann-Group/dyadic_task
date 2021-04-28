import pickle
import numpy as np
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import conf as c
import engine as e

def update(dt=0):
    reactor.callLater(1/c.pos_updates_ps, update)
    e.update(dt)
    server.send_ants(e.ant_posistions(), e.ant_radians())

class Server(DatagramProtocol):
    def startProtocol(self):
        self.player_1_addr=None
        reactor.callLater(1/c.pos_updates_ps, update)

    def datagramReceived(self, datagram, address):
        self.player_1_addr=address

    def send_ants(self, ant_pos, ant_rad):
        if ant_pos is not None and self.player_1_addr is not None:
            out=pickle.dumps(np.column_stack((ant_pos, ant_rad)))
            self.transport.write(out, self.player_1_addr)

e.load()
server=Server()
reactor.listenUDP(c.server_port, server)#, listenMultiple=True)
reactor.run()
