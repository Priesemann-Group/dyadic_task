import time
import pickle
import numpy as np
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from configuration import conf
from backend import engine, data_depositor
from backend.game_scheduler import GameScheduler

from threading import Thread

# TODO if server is closed a invalid game record is saved


class Server(DatagramProtocol):
    def __init__(self):
        self._player_addrs = [('', 0), ('', 0)]
        self._player_last_contact = [-1., -1.]
        self._player_pos = [(0, 0), (0, 0)]
        self._player_ping = [-1., -1.]
        self._player_scale_factor = [-1., -1.]

        engine.load()
        reactor.listenUDP(conf.server_port, self)

        Thread(target=self._run_reactor,
               kwargs={"installSignalHandlers": False}).start()

        self._game_scheduler = GameScheduler(self._tick)
        self._game_scheduler.start()  # blocking, sleeps until wakeup call

    def startProtocol(self):
        reactor.callLater(.5, self._check_player_contact)

    def datagramReceived(self, data, address):
        packet = pickle.loads(data)
        if isinstance(packet, bytes):
            self._process_message(packet, address)
        else:
            idx = self._player_addrs.index(address)
            self._consume_client_packet(packet, idx)

    def _process_message(self, msg, address):
        if msg == b'ping request':
            self.transport.write(pickle.dumps(b'ping request answer'), address)
        elif msg == b'disconnect':
            self._deregister_player(self._player_addrs.index(address))
        elif msg == b'connect':
            player_idx = self._register_new_player(address)
            self.transport.write(pickle.dumps(player_idx), address)
            self._game_scheduler.next_round()
            self._game_scheduler.wakeup()

    def _register_new_player(self, address):
        print(f'register new player is called, addr: {address}')
        for player_idx, lc in enumerate(self._player_last_contact):
            if lc < 0.:
                self._player_addrs[player_idx] = address
                self._player_last_contact[player_idx] = time.time()
                #self.new_round(reset=True)
                return player_idx
        # TODO send server is full message

    def _consume_client_packet(self, packet, client_idx):
        self._player_last_contact[client_idx] = time.time()
        x, y, ping, scale_factor = packet
        self._player_pos[client_idx] = (x, y)
        self._player_ping[client_idx] = ping
        self._player_scale_factor[client_idx] = scale_factor

    def _run_reactor(self, **kwargs):
        reactor.run(**kwargs)
        data_depositor.close()

    def _tick(self):
        game_state = engine.produce_next_game_state(self._player_pos)
        game_state = self._add_server_info(game_state)
        #print(game_state)
        self._send_packet(game_state)
        data_depositor.deposit(game_state)

    def _add_server_info(self, game_state):
        server_header = np.array([*self._player_scale_factor, time.time(), 0])  # last value is unused
        game_state[0, 3] = self._player_ping[0]
        game_state[1, 3] = self._player_ping[1]
        game_state = np.vstack((server_header, game_state))
        return game_state

    def _check_player_contact(self):
        t = time.time()
        for i, lc in enumerate(self._player_last_contact):
            if lc > 0. and t-lc > conf.time_until_disconnect:
                self._deregister_player(i)
        if self._player_last_contact[0] < 0. and self._player_last_contact[1] < 0.:
            self._game_scheduler.sleep()
        reactor.callLater(.5, self._check_player_contact)

    def _send_packet(self, game_state):
        packet = pickle.dumps(game_state)
        for i, addr in enumerate(self._player_addrs):
            if self._player_last_contact[i] > 0.:
                self.transport.write(packet, addr)

    def _deregister_player(self, player_idx):
        self._player_last_contact[player_idx] = -1.
        self._player_pos[player_idx] = (-1000, -1000)
        self._player_ping[player_idx] = -1
        self._player_scale_factor[player_idx] = -1.
        self._game_scheduler.next_round()


server = Server()
