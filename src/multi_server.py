import pickle
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from configuration import conf
from backend.lap_coordinator import LapCoordinator
from threading import Thread


class MultiServer(DatagramProtocol):
    def __init__(self):
        self._lap_coordinator = LapCoordinator(send_pkg=self._send_packet,
                                               send_msg=self._msg_to_all)
        self._ended = False
        reactor.listenUDP(conf.server_port, self)
        Thread(target=self._run_reactor,
               kwargs={"installSignalHandlers": False}).start()
        self._lap_coordinator.start()  # blocking until everything is recoded
        self._ended = True
        print('Recording was successful')

    def startProtocol(self):
        reactor.callLater(.5, self._check_player_contact)
        reactor.callLater(1, self._end_from_server_thread)

    def datagramReceived(self, data, address):
        packet = pickle.loads(data)
        if isinstance(packet, bytes):
            self._process_message(packet, address)
        else:
            self._lap_coordinator.consume_packet(packet, address)

    def _process_message(self, msg, address):
        if msg == b'ping request':
            self.transport.write(pickle.dumps(b'ping request answer'), address)
        elif msg == b'disconnect':
            print('INVALID RECORD: PLAYER DISCONNECTED')
        elif msg == b'connect':
            self._lap_coordinator.register_player(address)

    def _msg_to_all(self, msg):
        msg = pickle.dumps(msg)
        for address in self._lap_coordinator.addresses:
            self.transport.write(msg, address)

    def _run_reactor(self, **kwargs):
        reactor.run(**kwargs)

    def _send_packet(self, game_states, target_addresses):
        for i, gs in enumerate(game_states):
            packet = pickle.dumps(gs)
            for address in target_addresses[i]:
                self.transport.write(packet, address)

    def _check_player_contact(self):
        if not self._lap_coordinator.all_players_connected():
            print('INVALID RECORD: PLAYER TIMED OUT')
        reactor.callLater(.5, self._check_player_contact)

    def _end_from_server_thread(self):
        if self._ended:
            if reactor.running:
                reactor.stop()
        else:
            reactor.callLater(1, self._end_from_server_thread)


MultiServer()
