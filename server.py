import time
import pickle
import numpy as np
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import conf as c
import engine as e


class Server(DatagramProtocol):
    def __init__(self):
        self.player_addrs = [('empty', 4242), ('empty', 4242)]
        self.player_pos = [(0, 0), (0, 0)]
        self.player_last_contact = [-1., -1.]

    def startProtocol(self):
        reactor.callLater(1 / c.pos_updates_ps, update)

    def datagramReceived(self, data, addr):
        if not self.check_player_contact():  # if the first client connects the game loop starts again
            reactor.callLater(1 / c.pos_updates_ps, update)
        if addr not in self.player_addrs:
            for i, lc in enumerate(self.player_last_contact):
                if lc < 0.:
                    self.player_addrs[i] = addr
                    self.player_last_contact[i] = time.time()
                    self.player_pos[i] = pickle.loads(data)
                    self.transport.write(pickle.dumps(i), addr)
                    return
            # TODO send server is full message
        else:
            idx = self.player_addrs.index(addr)
            self.player_last_contact[idx] = time.time()
            self.player_pos[idx] = pickle.loads(data)

    def send_ants(self, ant_pos, ant_rad):
        if ant_pos is not None:
            target_state = e.get_target_state(self.player_pos)
            mouse_header = np.array([[*self.player_pos[0], target_state[0]],
                                     [*self.player_pos[1], target_state[1]]])
            score_header = np.array([*e.score, 0])  # last value is unused
            out = np.column_stack((ant_pos, ant_rad))
            out = np.vstack((mouse_header, score_header, out))
            out = pickle.dumps(out)
            for i, addr in enumerate(self.player_addrs):
                if self.player_last_contact[i] > 0.:
                    self.transport.write(out, addr)

    def check_player_contact(self):
        t = time.time()
        for i, lc in enumerate(self.player_last_contact):
            if t-lc > 15:
                self.player_last_contact[i] = -1.
                e.score[i] = 0
        return self.player_last_contact[0] > 0. or self.player_last_contact[1] > 0.


def update(dt=0):
    if server.check_player_contact():  # contact to at least one client
        reactor.callLater(1 / c.pos_updates_ps, update)
        e.update(dt)
        server.send_ants(e.pos, e.rad)


e.load()
server = Server()
reactor.listenUDP(c.server_port, server)
reactor.run()
