import time

import numpy as np

from configuration import conf as c
from pyglet.shapes import Circle
from pyglet.graphics import Batch, OrderedGroup
from ui.sounds import OccupationSoundPlayer
from ui.elements import TargetIndicator, Pointer, PopUpLabel, Ant
from ui.window import ScaleFieldWindow


class UI:
    def __init__(self, debug_overlay, on_motion, on_close):
        self._on_motion_func = on_motion
        self._on_close_func = on_close

        self._bg_group = OrderedGroup(0)
        self._ant_group = OrderedGroup(1)
        self._fg_group = OrderedGroup(2)
        self._target_group = OrderedGroup(3)

        self._batch = Batch()
        self._win = ScaleFieldWindow(batch=self._batch,
                                     bg_group=self._bg_group,
                                     fg_group=self._fg_group,
                                     debug_overlay=debug_overlay,
                                     resizable=True, vsync=False)

        # Ui elements
        self._player_circles = []
        self._target_indicators = []
        self._score_popup_labels = []
        self._occupation_sound_player = []
        self._init_ui_elements()

        self._player_idx = -2
        self._ants = self._generate_ants()

        # Register event handlers
        self._win.event(self.on_close)
        self._win.event(self.on_draw)
        self._win.event(self.on_mouse_motion)

    def set_values(self, pings, player_0_pos, player_1_pos, target_states,
                   score_states, scores, ant_pos, ant_kinds):
        self._win.set_scores_and_pings(scores, pings, score_states)
        self._player_circles[0].place(tuple(self._win.to_win_coordinates(player_0_pos)), self._win.get_scale_factor())
        self._player_circles[1].place(tuple(self._win.to_win_coordinates(player_1_pos)), self._win.get_scale_factor())
        self._set_ants(ant_pos=self._win.to_win_coordinates(ant_pos),
                       ant_rad=[c.ant_radius * self._win.get_scale_factor()] * c.ant_amount,  # shared radius
                       ant_kinds=ant_kinds)
        self._set_target_states(target_states, score_states)
        self._set_score_states(score_states, target_states)
        for popup in self._score_popup_labels:
            popup.adapt_size(self._win.get_scale_factor())

    def set_start_time(self, start_time):
        time_until_start = (start_time - time.time())
        if time_until_start < 0.:
            self._win.set_countdown(0)
        else:
            self._hide_ants()
            if time_until_start < c.time_before_round * 1 / 3:
                self._win.set_countdown(1)
            elif time_until_start < c.time_before_round * 2 / 3:
                self._win.set_countdown(2)
            else:
                self._win.set_countdown(3)

    def get_scale_factor(self):
        return self._win.get_scale_factor()

    def close_window(self):
        self._win.close()

    def on_close(self):
        self._on_close_func()

    def on_draw(self):
        self._win.on_draw()
        self._batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):  # Calls clients function to send position to server
        self._on_motion_func(tuple(self._win.to_win_coordinates((x, y), reverse=True)))

    def set_player_idx(self, player_idx):
        self._player_idx = player_idx
        self._win.set_player_idx(player_idx)

    def _init_ui_elements(self):
        for i in [0, 1]:
            marker_group = OrderedGroup(5 - i)
            player_group = OrderedGroup(7 - i)
            player_pointer_group = OrderedGroup(9 - i)
            player_color = c.player_colors[i]
            self._player_circles.append(Pointer(player_color=player_color,
                                                player_group=player_group,
                                                player_pointer_group=player_pointer_group,
                                                batch=self._batch))
            self._target_indicators.append(TargetIndicator(marker_group=marker_group,
                                                           batch=self._batch,
                                                           group=self._target_group))
            self._score_popup_labels.append(PopUpLabel(color=(*player_color, 255),
                                                       group=player_group,
                                                       batch=self._batch))
            self._occupation_sound_player.append(OccupationSoundPlayer(c.player_volumes[i]))

    def _generate_ants(self):
        ants = []
        for _ in range(c.ant_amount):
            ants.append(Ant(kind=np.nan,
                            batch=self._batch,
                            group=self._ant_group))
        return ants

    def _set_ants(self, ant_pos, ant_rad, ant_kinds):
        for i in range(c.ant_amount):
            self._ants[i].update_ant(ant_pos[i], ant_rad[i], ant_kinds[i])

    def _hide_ants(self):
        for ant in self._ants:
            ant.hide()
        for label in self._score_popup_labels:
            label.hide()
        for pointer in self._player_circles:
            pointer.hide()
        for indicator in self._target_indicators:
            indicator.hide()

    def _set_target_states(self, target_states, scored_states):  # Called after set_ants()
        for i in [0, 1]:
            if target_states[i] > -.5:  # we are on a target
                if self._target_indicators[i].x == -1000:  # just arrived on a new target
                    self._occupation_sound_player[i].occupying()
                idx = int(target_states[i])
                progress = target_states[i] - idx
                self._target_indicators[i].set_on_target(self._ants[idx], progress, player_idx=i)
            else:
                if self._target_indicators[i].x != -1000:  # target is away
                    if np.isnan(scored_states[i]):  # because we lost it
                        self._occupation_sound_player[i].slipped_off()
                    else:  # because we occupied it
                        self._occupation_sound_player[i].scored()
                self._target_indicators[i].move((-1000, -1000))

    def _set_score_states(self, score_states, target_states):
        if not np.isnan(sum(score_states)) \
                and int(target_states[0]) == int(target_states[1]) \
                and self._score_popup_labels[0].x == -1000:
            for i in [0, 1]:
                self._score_popup_labels[i].popup(self._player_circles[self._player_idx], int(score_states[i]))
            self._score_popup_labels[0].anchor_x = 'right'
        else:
            self._set_individual_score_states(score_states)
        self._update_popup_pos(score_states)

    def _set_individual_score_states(self, score_states):
        for i in [0, 1]:
            if not np.isnan(score_states[i]):
                if self._score_popup_labels[i].x == -1000:  # Scored!
                    self._score_popup_labels[i].popup(self._player_circles[i], int(score_states[i]))
            else:  # remove old score popup labels
                self._score_popup_labels[i].x = -1000
                self._score_popup_labels[i].anchor_x = 'left'

    def _update_popup_pos(self, score_states):
        for i in [0, 1]:
            if self._score_popup_labels[i].x != -1000:
                progress = score_states[i] - int(score_states[i])
                self._score_popup_labels[i].update(progress)