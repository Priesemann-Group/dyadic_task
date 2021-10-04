import sys
import time
import tables
from pyglet import app, clock
from pyglet.window import key
from configuration import conf
from ui.ui import UI
from pred.linear import Predictor

playback_speeds = [1/3, 2/3, 1, 4/3, 5/3, 2]


class Replay:
    def __init__(self):
        self._ui = UI(debug_overlay='debug' in sys.argv,
                      on_motion=None,
                      on_close=None,
                      on_player_ready=None,
                      replay=True)
        self._ui._win.event(self.on_key_press)
        self._running = True
        self._current_frame = 0
        self._replay_time = 0
        self._replay_start_time = time.time()
        self._last_frame_time = time.time()
        self._record = tables.open_file(sys.argv[1], mode='r').root.data
        self._timestamps = self._record[:, 0, 2]
        self._pb_speed = 2
        self._predictor = Predictor()
        clock.schedule_interval(self._tick, 2 ** -8)
        app.run()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            if not self._running:
                self._replay_start_time = time.time() - self._replay_time
            self._running = not self._running

        if modifiers == key.MOD_SHIFT:
            if symbol == key.A:
                self._change_playback(-1)
            elif symbol == key.D:
                self._change_playback(+1)
        else:
            if symbol == key.A:
                self._jump_backward()
            elif symbol == key.D:
                self._jump_forward()

    def _change_playback(self, val):
        self._pb_speed += val
        if self._pb_speed < 0:
            self._pb_speed = 0
        elif self._pb_speed == len(playback_speeds):
            self._pb_speed = len(playback_speeds) - 1

    def _jump_backward(self):
        secs_to_jump = conf.secs_jumps * playback_speeds[self._pb_speed]
        frames_to_jump = int(conf.pos_updates_ps * secs_to_jump)
        if self._current_frame > frames_to_jump:
            self._replay_start_time += secs_to_jump
            self._current_frame -= frames_to_jump

    def _jump_forward(self):
        secs_to_jump = conf.secs_jumps * playback_speeds[self._pb_speed]
        frames_to_jump = int(conf.pos_updates_ps * secs_to_jump)
        if self._current_frame < len(self._timestamps) - frames_to_jump:
            self._replay_start_time -= secs_to_jump
            self._current_frame += frames_to_jump

    def _tick(self, dx):
        if self._running:
            t = time.time()
            if t - self._last_frame_time > 1 / conf.pos_updates_ps / playback_speeds[self._pb_speed]:
                self._last_frame_time = t
                self._next_frame()

    def _next_frame(self):
        packet = self._record[self._current_frame]
        packet = packet[1:]  # throw first, general header away
        prediction = self._predictor.predict(
            ant_pos=packet[3:, :2],
            p0_pos=packet[0, :2],
            p1_pos=packet[1, :2])
        self._ui.set_values(
            player_0_pos=packet[0, :2],
            player_1_pos=packet[1, :2],
            target_states=list(packet[:2, 2]),
            score_states=list(packet[2, 2:]),
            scores=list(packet[2, :2]),
            pings=list(packet[:2, 3]),
            ant_pos=packet[3:, :2],
            ant_kinds=packet[3:, 2],
            prediction=prediction)
        self._current_frame += 1


Replay()
