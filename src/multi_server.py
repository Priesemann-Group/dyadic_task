import time
import pickle
import numpy as np
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from configuration import conf
from backend import data_depositor
from backend.engine import Engine
from backend.game_manager import GameManager
from backend.game_scheduler import MultiGameScheduler

from threading import Thread


class MultiServer(DatagramProtocol):
    def __init__(self):
        self._game_manager = GameManager()
        self._game_scheduler = MultiGameScheduler(action=self._tick,
                                                  send_msg=self._msg_to_all)

        reactor.listenUDP(conf.server_port, self)
        Thread(target=self._run_reactor,
               kwargs={"installSignalHandlers": False}).start()

        self._game_scheduler.start()  # blocking, sleeps until wakeup call

    def startProtocol(self):
        reactor.callLater(.5, self._check_player_contact)

    def datagramReceived(self, data, address):
        packet = pickle.loads(data)
        if isinstance(packet, bytes):
            self._process_message(packet, address)
        else:
            self._game_manager.consume_packet(packet, address)

    def _process_message(self, msg, address):
        if msg == b'ping request':
            self.transport.write(pickle.dumps(b'ping request answer'), address)
        elif msg == b'disconnect':
            print('DISCONNECT NOT IMPLEMENTED')  # TODO
        elif msg == b'connect':  # TODO server is full msg?
            self._game_manager.register_player(address)
            if self._game_manager.fully_staffed():
                self._game_scheduler.wakeup()

    def _msg_to_all(self, msg):
        msg = pickle.dumps(msg)
        if self._game_manager.fully_staffed():
            for address in self._game_manager.addresses:
                self.transport.write(msg, address)

    def _run_reactor(self, **kwargs):
        reactor.run(**kwargs)
        # data_depositor.close()  # TODO implement data depositor

    def _tick(self):
        game_states, target_addresses = self._game_manager.get_next_game_states()
        self._send_packet(game_states, target_addresses)
        # data_depositor.deposit(game_state) # TODO implement data depositor

    def _send_packet(self, game_states, target_addresses):
        print('send_packet called')
        for i, gs in enumerate(game_states):
            packet = pickle.dumps(gs)
            for address in target_addresses[i]:
                self.transport.write(packet, address)

    def _check_player_contact(self):
        if not self._game_manager.all_players_connected():
            print('PLAYER TIMED OUT')  # TODO
        reactor.callLater(.5, self._check_player_contact)


server = MultiServer()
