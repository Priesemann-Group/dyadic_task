from backend.engine import Engine
from backend.data_depositor import Depositor
import time
import numpy


class Match:  # contains data of player 0 and 1 for one game
    def __init__(self, output_folder, addresses, lap, p0_idx, p1_idx):
        self._addresses = addresses
        self._last_contact_times = [-1., -1.]
        self._positions = [(-1000, 0), (-1000, 0)]
        self._pings = [-1., -1.]
        self._scale_factors = [-1., -1.]
        self._identifier = str(lap * 100 + p0_idx * 10 + p1_idx).zfill(3)
        self._engine = Engine()
        self._depositor = Depositor(output_folder, self._identifier)

    def set_values(self, packet, address):
        player_idx = 0
        if address == self._addresses[1]:
            player_idx = 1
        x_pos, y_pos, ping, scale_factor = packet
        self._positions[player_idx] = (x_pos, y_pos)
        self._pings[player_idx] = ping
        self._scale_factors[player_idx] = scale_factor
        self._last_contact_times[player_idx] = time.time()

    def next_game_state(self):
        game_state = self._engine.produce_next_game_state(self._positions)
        game_state[0, 3] = self._pings[0]
        game_state[1, 3] = self._pings[1]
        info_header = numpy.array([*self.scale_factors, time.time(), float(int(self._identifier))])
        game_state = numpy.vstack((info_header, game_state))
        self._depositor.deposit(game_state)
        return game_state

    @property
    def addresses(self):
        return self._addresses

    @property
    def scale_factors(self):
        return self._scale_factors

    @property
    def last_contact_times(self):
        return self._last_contact_times

    @property
    def identifier(self):
        return self._identifier

    @addresses.setter
    def addresses(self, value):
        self._addresses = value

