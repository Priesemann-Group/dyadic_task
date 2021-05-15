import pickle
import sys
import time

import ui
import conf as c
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from threading import Thread
from queue import Queue

rec_packets = Queue()
player_number = None


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
        self.transport.write(pickle.dumps((0, 0, 0)))

    def send_mouse_pos(self, pos):
        self.transport.write(pickle.dumps((*pos, int(self.ping))))

    def request_ping(self, dx):
        self.ping_request_start = time.time()
        self.transport.write(pickle.dumps(b'ping request'))

    def datagramReceived(self, datagram, address):
        global player_number
        if player_number is None:
            player_number = pickle.loads(datagram)
            ui.player_number = player_number
            print(f'this client got player number: {player_number}')
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
    global player_number
    opponent_number = (player_number - 1) % 2
    target_states = [packet[0][2], packet[1][2]]
    score_states = list(packet[2][2:].astype(float))
    if player_number == 1:  # In this case we are the second player
        target_states.reverse()
        score_states.reverse()
    ui.scores = list(packet[2][:2].astype(float))
    ui.player_pings = list(packet[:2, 3])
    packet[:, :3] *= ui.scale_factor  # scale positions as well as radians
    ui.player_mouse_circles[0].position = tuple(packet[player_number][:2] + ui.origin_coords)
    ui.player_mouse_circles[1].position = tuple(packet[opponent_number][:2] + ui.origin_coords)
    ui.set_ants(packet[3:])
    ui.set_target_states(target_states)  # should be called after set_ants()
    ui.set_score_states(score_states)


client = UdpClient()


@ui.win.event
def on_mouse_motion(x, y, dx, dy):  # TODO handle high res input
    client.send_mouse_pos(((x - ui.origin_coords[0]) / ui.scale_factor,
                           (y - ui.origin_coords[1]) / ui.scale_factor))


reactor.listenUDP(0, client)
Thread(target=reactor.run,
       kwargs={"installSignalHandlers": False},
       ).start()

ui.schedule_interval(consume_packet, 2 ** -8)
ui.schedule_interval(client.request_ping, .5)
ui.run()
