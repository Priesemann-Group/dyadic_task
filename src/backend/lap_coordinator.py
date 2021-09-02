from time import sleep
import configuration.conf as conf
from backend.match import Match
from backend import data_depositor
import time
import itertools
from sched import scheduler as Scheduler


class LapCoordinator:
    def __init__(self, send_pkg, send_msg):
        self._matches = []
        self._addresses = []
        self._send_pkg = send_pkg
        self._send_msg = send_msg

    def start(self):
        while len(self._addresses) != 2 * conf.simultaneous_games:
            sleep(.1)
        self._run()

    def consume_packet(self, packet, address):
        for match in self._matches:
            if address in match.addresses:
                match.set_values(packet, address)
                break

    def register_player(self, address):
        if address not in self._addresses:
            self._addresses.append(address)

    def send_next_game_states(self):
        game_states = []
        target_addresses = []
        for match in self._matches:
            game_states.append(match.next_game_state())
            target_addresses.append(match.addresses)
        self._send_pkg(game_states, target_addresses)

    def all_players_connected(self):
        t = time.time()
        for match in self._matches:
            for last_contact in match.last_contact_times:
                if last_contact > 0. and t - last_contact > conf.time_until_disconnect:
                    return False
        return True

    def _run(self):
        output_folder = data_depositor.create_parallel_game_folder()
        summed_scores = [0] * conf.simultaneous_games * 2
        for lap, lc in enumerate(lap_constellations()):
            if lap >= conf.laps_to_play:
                break
            for p0_idx, p1_idx in lc:
                self._matches.append(Match(output_folder=output_folder,
                                           addresses=[self._addresses[p0_idx], self._addresses[p1_idx]],
                                           lap=lap,
                                           p0_idx=p0_idx,
                                           p1_idx=p1_idx))
            self._run_lap()
            for match in self._matches:
                p0_score, p1_score = match.get_score()
                summed_scores[match.p0_idx] += p0_score
                summed_scores[match.p1_idx] += p1_score
            self._matches = []
        for i in range(len(summed_scores)):
            print(f'player {i}\'s score: {summed_scores[i]}')
        self._send_msg(b'Recording session ended successfully')

    def _run_lap(self):
        scheduler = Scheduler(time.time, time.sleep)
        start_time = conf.time_before_round + time.time()
        self._send_msg(start_time)
        for i in range(conf.update_amount):
            _ = scheduler.enterabs(start_time + i / conf.pos_updates_ps, 1, self.send_next_game_states)
        scheduler.run()

    @property
    def addresses(self):
        return self._addresses


def has_no_duplicate_player(lap):
    players = []
    for match in lap:
        for p in list(match):
            if p in players:
                return False
            players.append(p)
    return True


def get_possible_laps():
    player_numbers = list(range(conf.simultaneous_games * 2))
    player_pairs = list(itertools.combinations(player_numbers, 2))
    all_combinations = list(itertools.combinations(player_pairs, conf.simultaneous_games))
    all_possible_laps = []
    for combination in all_combinations:
        if has_no_duplicate_player(combination):
            all_possible_laps.append(combination)
    return all_possible_laps


def lap_constellations():
    all_possible_laps = get_possible_laps()
    laps_without_repeated_match = []
    existing_matches = set()
    for lap in all_possible_laps:
        if not set(lap).intersection(existing_matches):
            existing_matches.update(set(lap))
            laps_without_repeated_match.append(list(lap))
    return laps_without_repeated_match
