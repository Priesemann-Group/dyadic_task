import time
import pickle
import numpy as np
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from configuration import conf as c
from backend import engine as e, data_depositor


class Server(DatagramProtocol):
    def __init__(self):
        self.player_addrs = [('', 0), ('', 0)]
        self.player_last_contact = [-1., -1.]
        self.player_pos = [(0, 0), (0, 0)]
        self.player_ping = [-1., -1.]
        self.player_scale_factor = [-1., -1.]
        self.past_update_count = 0

        # TODO debug
        self.last_update_call = -1
        self.update_time_diff_moving_avg = 0.

        data_depositor.new_file()
        e.update(0)
        self.game_state = self.get_game_state()

        e.load()
        reactor.listenUDP(c.server_port, self)
        reactor.run()
        data_depositor.close()

    def startProtocol(self):
        reactor.callLater(1 / c.pos_updates_ps, self.update)

    def datagramReceived(self, data, addr):
        packet = pickle.loads(data)
        if isinstance(packet, bytes):
            self.process_message(packet, addr)
        else:
            idx = self.player_addrs.index(addr)
            self.consume_client_packet(packet, idx)

    def process_message(self, msg, addr):
        if msg == b'ping request':
            self.transport.write(pickle.dumps(b'ping request answer'), addr)
        elif msg == b'disconnect':
            self.deregister_player(self.player_addrs.index(addr))
        elif msg == b'connect':
            if not self.check_player_contact():  # if the first client connects the game loop starts again
                self.last_update_call = -1  # TODO
                reactor.callLater(1 / c.pos_updates_ps, self.update)
            player_idx = self.register_new_player(addr)
            self.transport.write(pickle.dumps(player_idx), addr)

    def register_new_player(self, addr):
        print(f'register new player is called, addr: {addr}')
        for player_idx, lc in enumerate(self.player_last_contact):
            if lc < 0.:
                self.player_addrs[player_idx] = addr
                self.player_last_contact[player_idx] = time.time()
                self.new_round(reset=True)
                return player_idx
        # TODO send server is full message

    def new_round(self, reset=False):
        self.past_update_count = 0
        if reset and data_depositor.file is not None:
            data_depositor.close()  # To delete invalid game recording
        data_depositor.new_file()
        e.respawn_ants()
        e.score = [0, 0]

    def consume_client_packet(self, packet, client_idx):
        self.player_last_contact[client_idx] = time.time()
        x, y, ping, scale_factor = packet
        self.player_pos[client_idx] = (x, y)
        self.player_ping[client_idx] = ping
        self.player_scale_factor[client_idx] = scale_factor

    def send_packet(self, game_state):
        packet = pickle.dumps(game_state)
        for i, addr in enumerate(self.player_addrs):
            if self.player_last_contact[i] > 0.:
                self.transport.write(packet, addr)

    def check_player_contact(self):
        t = time.time()
        for i, lc in enumerate(self.player_last_contact):
            if lc > 0. and t-lc > c.time_until_disconnect:
                self.deregister_player(i)
        still_contact = self.player_last_contact[0] > 0. or self.player_last_contact[1] > 0.
        return still_contact

    def deregister_player(self, player_idx):
        self.player_last_contact[player_idx] = -1.
        self.player_pos[player_idx] = (-1000, -1000)
        self.player_ping[player_idx] = -1
        self.player_scale_factor[player_idx] = -1.
        self.new_round(reset=True)
        e.score[player_idx] = 0

    def get_game_state(self):
        target_state = e.get_target_state(self.player_pos)
        general_header = np.array([*self.player_scale_factor, 0, 0])  # last value is unused
        player_header = np.array([[*self.player_pos[0], target_state[0], self.player_ping[0]],
                                  [*self.player_pos[1], target_state[1], self.player_ping[1]]])
        score_header = np.array([*e.score, *e.score_state])
        game_state = np.column_stack((e.pos, e.rad, e.shares))
        game_state = np.vstack((general_header, player_header, score_header, game_state))

        return game_state

    def update(self, dt=0):
        if self.last_update_call < 0.:
            self.last_update_call = time.time()
            print('hallo')
        t = time.time()
        time_diff = t-self.last_update_call
        print(f'time_diff {time_diff}')
        self.update_time_diff_moving_avg = .7 * self.update_time_diff_moving_avg + .3 * time_diff
        print(self.update_time_diff_moving_avg)
        self.last_update_call = t

        self.game_state[0, 2] = time.time()  # set output timestamp in general_header
        self.send_packet(self.game_state)

        if self.check_player_contact():  # contact to at least one client

            time_since_start = time.time() - t
            wait_time = 1 / c.pos_updates_ps - time_since_start
            print(self.update_time_diff_moving_avg)
            if (self.update_time_diff_moving_avg - 1/c.pos_updates_ps) > 0.:
                wait_time -= self.update_time_diff_moving_avg - 1/c.pos_updates_ps

            reactor.callLater(wait_time, self.update)

            self.past_update_count += 1
            if self.past_update_count == c.update_amount:
                self.new_round()
            data_depositor.deposit(self.game_state)
            e.update(dt)
            self.game_state = self.get_game_state()


server = Server()
