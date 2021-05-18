import pickle
import sys
import time

from ui import UI
import conf as c
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from threading import Thread
from queue import Queue

from pyglet import app, clock

rec_packets = Queue()
player_idx = None
opponent_idx = None


class UdpClient(DatagramProtocol):

    def __init__(self):
        self.ping = 0.
        self.ping_request_start = -1.

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        if len(sys.argv) == 2 and sys.argv[1] == 'local':
            self.transport.connect('127.0.0.1', c.server_port)
        else:
            self.transport.connect(c.server_ip, c.server_port)
        self.transport.write(pickle.dumps((0, 0, 0, 0)))

    def send_mouse_pos(self, pos):
        self.transport.write(pickle.dumps((*pos, int(self.ping), ui.get_scale_factor())))

    def request_ping(self, dx):
        self.ping_request_start = time.time()
        self.transport.write(pickle.dumps(b'ping request'))

    def datagramReceived(self, datagram, address):
        global player_idx, opponent_idx
        if player_idx is None:
            player_idx = pickle.loads(datagram)
            opponent_idx = (player_idx - 1) % 2
            ui.set_player_idx(player_idx)
            print(f'this client got player number: {player_idx}')
        else:
            packet = pickle.loads(datagram)
            if str(packet) == str(b'ping request answer'):
                self.ping = (time.time() - self.ping_request_start) * 1000  # in milliseconds
                self.ping_request_start = -1.
            else:
                rec_packets.put(packet)

    def connectionRefused(self):
        print("No one listening")


def get_newest_packet():
    if rec_packets.qsize() > 1:
        print(f'Client skipped {rec_packets.qsize() - 1} packet(s).')
        for _ in range(rec_packets.qsize() - 1):
            rec_packets.get()
    return rec_packets.get()


def consume_packet(dx):
    packet = get_newest_packet()
    packet = packet[1:]  # throw first, general header away
    target_states = list(packet[:2, 2])
    score_states = list(packet[2, 2:])
    if player_idx == 1:  # In this case we are the second player
        target_states.reverse()
        score_states.reverse()
    ui.set_values(
        player_pos=packet[player_idx, :2],
        opponent_pos=packet[opponent_idx, :2],
        target_states=target_states,
        score_states=score_states,
        scores=list(packet[2, :2]),
        pings=list(packet[:2, 3]),
        ant_pos=packet[3:, :2],
        ant_rad=packet[3:, 2],
        ant_shares=packet[3:, 3])


client = UdpClient()
ui = UI(debug_overlay=True,
        on_motion=client.send_mouse_pos)

reactor.listenUDP(0, client)
Thread(target=reactor.run,
       kwargs={"installSignalHandlers": False},).start()

clock.schedule_interval(consume_packet, 2 ** -8)
clock.schedule_interval(client.request_ping, .5)
app.run()
