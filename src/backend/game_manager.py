import configuration.conf as conf
from backend.engine import Engine
from backend.data_depositor import Depositor
from backend import data_depositor
import time, numpy


class GameManager:
    class Game:  # contains data of player 0 and 1 for one game
        def __init__(self, output_folder, addresses, lap, p0_idx, p1_idx):
            self._addresses = addresses
            self._last_contact_times = [-1., -1.]
            self._positions = [(-1000, 0), (-1000, 0)]
            self._pings = [-1., -1.]
            self._scale_factors = [-1., -1.]
            self._identifier = str(lap * 100 + p0_idx * 10 + p1_idx).zfill(3)
            self._engine = Engine()
            self._depositor = Depositor(output_folder, self._identifier)
            self._engine.spawn_ants()  # TODO Move into engine constructor

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

        #def set_identifier(self, lap, client_0_idx, client_1_idx):
        #    self._identifier = lap * 100 + client_0_idx * 10 + client_1_idx

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

    def __init__(self):
        self._games = []
        self._addresses = []
        self._lap = 0  # TODO

    def consume_packet(self, packet, address):
        for game in self._games:
            if address in game.addresses:
                game.set_values(packet, address)
                break

    def register_player(self, address):
        if address not in self._addresses:
            self._addresses.append(address)
        if self.fully_staffed():
            self._start_games()
            # pass  # TODO start rounds if all ready

    def fully_staffed(self):
        return len(self._addresses) == 2 * conf.simultaneous_games

    def get_next_game_states(self):
        game_states = []
        target_addresses = []
        for game in self._games:
            game_states.append(game.next_game_state())
            target_addresses.append(game.addresses)
        return game_states, target_addresses

    def all_players_connected(self):
        t = time.time()
        for game in self._games:
            for last_contact in game.last_contact_times:
                if last_contact > 0. and t - last_contact > conf.time_until_disconnect:
                    return False
        return True

    def _start_games(self):
        output_folder = data_depositor.create_parallel_game_folder()
        for i in range(1, 2 * conf.simultaneous_games, 2):
            print(f'start_game loop {i}')
            self._games.append(self.Game(output_folder=output_folder,
                                         addresses=[self._addresses[i-1], self._addresses[i]],
                                         lap=self._lap,
                                         p0_idx=i-1,
                                         p1_idx=i))

    @property
    def addresses(self):
        return self._addresses

