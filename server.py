import time
import pickle
import numpy as np
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import conf as c
import engine as e
import data_depositor

# TODO handle client disconnects


class Server(DatagramProtocol):
    def __init__(self):
        self.player_addrs = [('empty', 4242), ('empty', 4242)]
        self.player_pos = [(0, 0), (0, 0)]
        self.player_last_contact = [-1., -1.]
        self.player_ping = [-1., -1.]
        self.past_update_count = 0

    def startProtocol(self):
        reactor.callLater(1 / c.pos_updates_ps, update)

    def datagramReceived(self, data, addr):

        packet = pickle.loads(data)
        if packet == b'ping request':
            self.transport.write(pickle.dumps(b'ping request answer'), addr)
            return

        if not self.check_player_contact():  # if the first client connects the game loop starts again
            reactor.callLater(1 / c.pos_updates_ps, update)

        if addr not in self.player_addrs:  # unknown player, try to register
            for i, lc in enumerate(self.player_last_contact):
                if lc < 0.:  # register new player
                    self.player_addrs[i] = addr
                    self.consume_client_packet(packet, i)
                    self.transport.write(pickle.dumps(i), addr)
                    self.new_round(reset=True)
                    return
            # TODO send server is full message
        else:
            idx = self.player_addrs.index(addr)
            self.consume_client_packet(packet, idx)

    def new_round(self, reset=False):
        self.past_update_count = 0
        if reset and data_depositor.file is not None:
            data_depositor.close()
        data_depositor.new_file()
        e.respawn_ants()
        e.score = [0, 0]

    def consume_client_packet(self, packet, client_idx):
        self.player_last_contact[client_idx] = time.time()
        x, y, ping = packet
        self.player_pos[client_idx] = (x, y)
        self.player_ping[client_idx] = ping

    def send_packet(self, game_state):
        packet = pickle.dumps(game_state)
        for i, addr in enumerate(self.player_addrs):
            if self.player_last_contact[i] > 0.:
                self.transport.write(packet, addr)

    def check_player_contact(self):
        t = time.time()
        for i, lc in enumerate(self.player_last_contact):
            if t-lc > c.time_until_disconnect:
                self.player_last_contact[i] = -1.
                e.score[i] = 0
        return self.player_last_contact[0] > 0. or self.player_last_contact[1] > 0.


e.load()
#data_depositor.init()
server = Server()


def get_game_state():
    target_state = e.get_target_state(server.player_pos)
    mouse_header = np.array([[*server.player_pos[0], target_state[0], server.player_ping[0]],
                             [*server.player_pos[1], target_state[1], server.player_ping[1]]])
    score_header = np.array([*e.score, 0, 0])  # 0 values are currently unused
    game_state = np.column_stack((e.pos, e.rad, e.shares))
    game_state = np.vstack((mouse_header, score_header, game_state))
    return game_state
    #  game_state = pickle.dumps(game_state)


def update(dt=0):
    if server.check_player_contact():  # contact to at least one client
        reactor.callLater(1 / c.pos_updates_ps, update)
        server.past_update_count += 1
        if server.past_update_count == c.update_amount:
            server.new_round()
        e.update(dt)
        game_state = get_game_state()
        server.send_packet(game_state)
        data_depositor.deposit(game_state)


reactor.listenUDP(c.server_port, server)
reactor.run()
data_depositor.close()
