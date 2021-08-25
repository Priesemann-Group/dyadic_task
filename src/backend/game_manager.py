import configuration.conf as conf
from backend.engine import Engine
import time, numpy


class GameManager:
    class Game:  # contains data of player 0 and 1 for one game
        def __init__(self):
            self._addresses = [None, None]
            self._last_contact_times = [-1., -1.]
            self._positions = [(-1000, 0), (-1000, 0)]
            self._pings = [-1., -1.]
            self._scale_factors = [-1., -1.]
            self._engine = Engine()

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
            info_header = numpy.array([*self.scale_factors, time.time(), 0])  # last value is unused
            game_state = numpy.vstack((info_header, game_state))
            return game_state

        def start_engine(self):
            self._engine.spawn_ants()

        @property
        def addresses(self):
            return self._addresses

        @property
        def scale_factors(self):
            return self._scale_factors

        @property
        def last_contact_times(self):
            return self._last_contact_times

        @addresses.setter
        def addresses(self, value):
            self._addresses = value

    def __init__(self):
        self._games = []
        self._addresses = []
        for _ in range(conf.simultaneous_games):
            self._games.append(self.Game())

    def consume_packet(self, packet, address):
        for game in self._games:
            if address in game.addresses:
                game.set_values(packet, address)
                break

    def register_player(self, address):
        if address not in self._addresses:
            self._addresses.append(address)
        if self.fully_staffed():
            self._parse_addresses_and_start()
            # pass  # TODO start rounds if all ready

    def fully_staffed(self):
        print(f'fully_stafed called :{len(self._addresses) == 2 * conf.simultaneous_games}')
        return len(self._addresses) == 2 * conf.simultaneous_games

    def get_next_game_states(self):
        game_states = []
        target_addresses = []
        for game in self._games:
            game_states.append(game.next_game_state())
            target_addresses.append(game.addresses)
        return game_states, target_addresses

    def get_all_addresses(self):
        addresses = []
        for game in self._games:
            addresses = addresses + game.addresses
        return addresses

    def all_players_connected(self):
        t = time.time()
        for game in self._games:
            for last_contact in game.last_contact_times:
                if last_contact > 0. and t - last_contact > conf.time_until_disconnect:
                    return False
        return True

    def _parse_addresses_and_start(self):
        i = 1
        for game in self._games:
            game.addresses = [self._addresses[i-1], self._addresses[i]]
            game.start_engine()
            i += 2
        print(f'should not be empty: {self._addresses}')
