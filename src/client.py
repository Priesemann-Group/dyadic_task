import pickle
import sys
import time
import numpy

from ui.ui import UI
from configuration import conf as c
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from threading import Thread
from queue import Queue

from pyglet import app, clock


class UdpClient(DatagramProtocol):
    def __init__(self):
        self._ping = 0.
        self._ping_request_start = -1.
        self._rec_packets = Queue()
        self._end_reactor_thread = False
        self._player_idx = -1
        self._opponent_idx = None
        self._next_round_start = -1.
        self._ui = UI(debug_overlay='debug' in sys.argv,
                      on_motion=self._send_mouse_pos,
                      on_close=self._close_form_ui_thread)

        reactor.listenUDP(0, self)
        Thread(target=reactor.run,
               kwargs={"installSignalHandlers": False}).start()

        clock.schedule_interval(self._consume_packet, 2 ** -8)
        clock.schedule_interval(self._request_ping, .5)
        app.run()

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        if 'local' in sys.argv:
            self.transport.connect('127.0.0.1', c.server_port)
        else:
            self.transport.connect(c.server_ip, c.server_port)
        self._send(b'connect')
        self._check_if_ui_exits()

    def datagramReceived(self, datagram, address):
        packet = pickle.loads(datagram)
        if isinstance(packet, int) and self._player_idx == -1:
            self._set_player_idx(index=packet)
        elif isinstance(packet, numpy.ndarray):
            self._rec_packets.put(packet)
        elif isinstance(packet, bytes):
            self._process_msg(msg=packet)
        elif isinstance(packet, float):
            self._next_round_start = packet

    def _set_player_idx(self, index):
        self._player_idx = index
        self._opponent_idx = (self._player_idx - 1) % 2
        self._ui.set_player_idx(self._player_idx)
        print(f'This client got player number: {self._player_idx}.')

    def _process_msg(self, msg):
        if str(msg) == str(b'ping request answer'):
            self._ping = (time.time() - self._ping_request_start) * 1000  # in milliseconds
            self._ping_request_start = -1.
        elif str(msg) == str(b'server is full'):
            print('Server is full.')
            self._close()

    def connectionRefused(self):
        print("Connection Refused.")
        self._close()

    def _check_if_ui_exits(self):
        if self._end_reactor_thread:
            self._send(b'disconnect')
            self._close()
        reactor.callLater(.2, self._check_if_ui_exits)

    def _send_mouse_pos(self, pos):
        self._send((*pos, int(self._ping), self._ui.get_scale_factor()))

    def _request_ping(self, dx):
        self._ping_request_start = time.time()
        self._send(b'ping request')

    def _send(self, packet):
        if self.transport is not None:  # transport is None if server is closed
            self.transport.write(pickle.dumps(packet))
        else:
            print('No connection to server.')
            self._close()

    def _get_newest_packet(self):
        if self._rec_packets.qsize() > 1:
            print(f'Client skipped {self._rec_packets.qsize() - 1} packet(s).')
            for _ in range(self._rec_packets.qsize() - 1):
                self._rec_packets.get()
        return self._rec_packets.get()

    def _close(self):
        self._ui.close_window()
        reactor.stop()

    def _close_form_ui_thread(self):
        self._end_reactor_thread = True

    def _consume_packet(self, dx):
        if self._next_round_start > 0:
            self._ui.set_start_time(self._next_round_start)
            if self._next_round_start - time.time() < 0.:
                self._next_round_start = -1
                self._ui.set_start_time(-1)
        elif self._rec_packets.qsize() > 0:
            packet = self._get_newest_packet()
            packet = packet[1:]  # throw first, general header away
            target_states = list(packet[:2, 2])
            score_states = list(packet[2, 2:])
            self._ui.set_values(
                player_0_pos=packet[0, :2],
                player_1_pos=packet[1, :2],
                target_states=target_states,
                score_states=score_states,
                scores=list(packet[2, :2]),
                pings=list(packet[:2, 3]),
                ant_pos=packet[3:, :2],
                ant_kinds=packet[3:, 2])


client = UdpClient()
