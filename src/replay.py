from ui.ui import UI
import sys
import tables
import time
from pyglet import app, clock


class Replay:
    def __init__(self):
        self._ui = UI(debug_overlay='debug' in sys.argv,
                      on_motion=None,
                      on_close=None,
                      on_player_ready=None,
                      replay=True)
        self._current_frame = 0
        file = tables.open_file(sys.argv[1], mode='r')
        self._record = file.root.data
        self._timestamps = self._record[:, 0, 2]
        self._replay_start_time = time.time()
        clock.schedule_interval(self._tick, 2 ** -8)
        app.run()

    def _tick(self, dx):
        t = time.time()
        next_frame_time = self._timestamps[self._current_frame] - self._timestamps[0]
        replay_time = t - self._replay_start_time
        if next_frame_time < replay_time:
            self._next_frame()

    def _next_frame(self):
        packet = self._record[self._current_frame]
        packet = packet[1:]  # throw first, general header away
        self._ui.set_values(
            player_0_pos=packet[0, :2],
            player_1_pos=packet[1, :2],
            target_states=list(packet[:2, 2]),
            score_states=list(packet[2, 2:]),
            scores=list(packet[2, :2]),
            pings=list(packet[:2, 3]),
            ant_pos=packet[3:, :2],
            ant_kinds=packet[3:, 2])
        self._current_frame += 1


Replay()
