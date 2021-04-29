import pickle
import numpy as np
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import conf as c
import engine as e


def update(dt=0):
    reactor.callLater(1 / c.pos_updates_ps, update)
    e.update(dt)
    server.send_ants(e.pos, e.rad)


class Server(DatagramProtocol):
    def __init__(self):
        self.player_pos = [(0, 0), (0, 0)]
        self.player_addrs = []
        self.mouse_pos = (0, 0)
        self.player_1_addr = None

    def startProtocol(self):
        reactor.callLater(1 / c.pos_updates_ps, update)

    def datagramReceived(self, data, addr):
        if addr not in self.player_addrs:
            if len(self.player_addrs) < 2:
                self.player_addrs.append(addr)
                idx = self.player_addrs.index(addr)
                print(idx)
                self.player_pos[idx] = pickle.loads(data)
                self.transport.write(pickle.dumps(idx), addr)
            else:
                return  # TODO
        else:
            idx = self.player_addrs.index(addr)
            self.player_pos[idx] = pickle.loads(data)

    def send_ants(self, ant_pos, ant_rad):
        if ant_pos is not None and len(self.player_addrs) > 0:
            target_state = e.get_target_state(self.player_pos)
            mouse_header = np.array([[*self.player_pos[0], target_state[0]],
                                     [*self.player_pos[1], target_state[1]]])
            score_header = np.array([*e.score, 0])  # last value is unused
            out = np.column_stack((ant_pos, ant_rad))
            out = np.vstack((mouse_header, score_header, out))
            out = pickle.dumps(out)
            for addr in self.player_addrs:
                self.transport.write(out, addr)


e.load()
server = Server()
reactor.listenUDP(c.server_port, server)
reactor.run()
