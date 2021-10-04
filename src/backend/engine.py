import random
import time

import numpy as np
from numba import njit

import configuration.conf as conf
import backend.ant_kind as ant_kind


class Engine:
    def __init__(self):
        self._pos = np.full((conf.ant_amount, 2), np.nan, dtype='float64')
        self._vel = np.full((conf.ant_amount, 2), np.nan, dtype='float64')
        self._kinds = []

        self._spawn_ants()

        self._score = [0, 0]
        self._score_state = [np.nan, np.nan]
        self._score_animation_end = [0., 0.]

        self._target_idx = [-1, -1]
        self._target_occupation_date = [0., 0.]

        self._collided_last_iter = []

    def produce_next_game_state(self, player_positions):
        self._update()
        target_state = self._get_target_state(player_positions)
        player_header = np.array([[*player_positions[0], target_state[0], 0],  # zeros are player pings later on
                                  [*player_positions[1], target_state[1], 0]])
        score_header = np.array([*self._score, *self._score_state])
        game_state = np.column_stack((self._pos, self._get_kinds(), np.zeros(conf.ant_amount)))
        game_state = np.vstack((player_header, score_header, game_state))
        return game_state

    @property
    def score(self):
        return self._score

    def _spawn_ants(self):
        self._score = [0, 0]
        self._pos = np.full((conf.ant_amount, 2), np.nan, dtype='float64')
        self._vel = np.full((conf.ant_amount, 2), np.nan, dtype='float64')
        # idx 0,1 coop_p1, idx 2,3 coop_p0, idx 4,5 comp
        self._kinds = [0, 0, 3, 3, 6, 6]  # will be overridden
        for i in range(conf.ant_amount):
            self._replace_ant(i)

    def _get_target_state(self, mouse_positions):
        out = [-1, -1]
        occupations = {}
        for player_idx, mouse_pos in enumerate(mouse_positions):
            mouse_pos = np.array(mouse_pos)
            if self._target_idx[player_idx] != -1:  # mouse was on a target
                dist = euclid_dist(self._pos[self._target_idx[player_idx]] - mouse_pos)
                if dist < conf.ant_radius:  # mouse is still on the target
                    t = time.time()
                    if t > self._target_occupation_date[player_idx]:  # occupied the target
                        occupations[player_idx] = self._target_idx[player_idx]
                    else:  # not occupied jet
                        time_left = self._target_occupation_date[player_idx] - t
                        out[player_idx] = self._target_idx[player_idx] + time_left / conf.time_to_occupy
                else:  # mouse was on a target but lost it
                    self._target_idx[player_idx] = -1
                    self._target_occupation_date[player_idx] = 0.
            else:  # mouse was on no target, check if it is now
                self._check_for_target(player_idx, mouse_pos)

        return self._consume_occupation_dict(occupations, out)

    def _consume_occupation_dict(self, occupations, out):
        if len(occupations) == 2 and occupations[0] == occupations[1]:  # Both players occupied the same target
            if ant_kind.is_shared(self._kinds[self._target_idx[0]]):
                out = self._consume_shared_target(out)
            else:  # Edge case: Both players occupied a not shared target within the same time (< 1/60s)
                if self._target_occupation_date[0] < self._target_occupation_date[1]:  # TODO not tested jet
                    out[1] = float(self._occupied(1))
                else:
                    out[0] = float(self._occupied(0))
        else:  # Consume occupations
            for player_idx in occupations.keys():
                out[player_idx] = float(self._occupied(player_idx))
        return out

    def _consume_shared_target(self, out):
        score_gain = list(ant_kind.get_score(self._kinds[self._target_idx[0]]))
        t = time.time()
        for i in [0, 1]:
            self._score_state[i] = score_gain[i] + .999
            self._score[i] += int(self._score_state[i])
            self._score_animation_end[i] = t + conf.occupied_animation_time
            out[i] = -1 * self._target_idx[i]
        self._replace_ant(self._target_idx[0])
        for i in [0, 1]:
            self._target_idx[i] = -1
            self._target_occupation_date[i] = 0.
        return out

    def _occupied(self, player_idx):
        if not ant_kind.is_shared(self._kinds[self._target_idx[player_idx]]):
            reward = ant_kind.get_score(self._kinds[self._target_idx[player_idx]])
            self._score[player_idx] += reward
            self._score_state[player_idx] = reward + .999
            self._score_animation_end[player_idx] = time.time() + conf.occupied_animation_time

            self._replace_ant(self._target_idx[player_idx])

            target = self._target_idx[player_idx]
            self._target_idx[player_idx] = -1
            self._target_occupation_date[player_idx] = 0.
            return target
        else:
            return self._target_idx[player_idx]

    def _check_for_target(self, i, mouse_pos):
        for k, p in enumerate(self._pos):
            dist = euclid_dist(p - mouse_pos)
            is_shared = ant_kind.is_shared(self._kinds[k])
            is_occupied_by_opponent = self._target_idx[(i - 1) % 2] == k
            if dist < conf.ant_radius and (is_shared or not is_occupied_by_opponent):
                self._target_idx[i] = k
                self._target_occupation_date[i] = time.time() + conf.time_to_occupy

    def _get_kinds(self):
        return np.array(self._kinds, dtype='float64')

    def _update(self):
        if conf.ant_movement:
            self._pos += self._vel
        self._collisions()
        self._correct_to_boundaries()
        self._update_animations()

    def _collisions(self):
        colls = _collision_calc(self._pos)
        for i, k in colls:
            if i == -1:
                break
            if tuple(sorted((i, k))) in self._collided_last_iter:
                if self._collision_next_iter(i, k):
                    continue
                else:
                    self._collided_last_iter.remove(tuple(sorted((i, k))))
            joint_vel = self._vel[i] + self._vel[k]
            self._vel[i] = joint_vel - self._vel[i]
            self._vel[k] = joint_vel - self._vel[k]
            if self._collision_next_iter(i, k):
                self._collided_last_iter.append(tuple(sorted((i, k))))

    def _correct_to_boundaries(self):
        for i in range(conf.ant_amount):
            if not np.isnan(self._pos[i][0]):
                for axis in [0, 1]:
                    if self._pos[i][axis] < 0 + conf.ant_radius:
                        self._pos[i][axis] = 1 + conf.ant_radius
                        self._vel[i][axis] *= -1
                    elif self._pos[i][axis] > conf.field_size[axis] - conf.ant_radius:
                        self._pos[i][axis] = conf.field_size[axis] - 1 - conf.ant_radius
                        self._vel[i][axis] *= -1

    def _update_animations(self):
        t = time.time()
        for i in [0, 1]:
            if not np.isnan(self._score_state[i]):
                time_left = self._score_animation_end[i] - t
                if time_left < 0:  # Animation is expired
                    self._score_state[i] = np.nan
                else:
                    self._score_state[i] = time_left / conf.occupied_animation_time + int(self._score_state[i])

    def _collision_next_iter(self, i, k):
        diff = (self._pos[i] - self._vel[i]) - (self._pos[k] - self._vel[k])
        return euclid_dist(diff) < 2 * conf.ant_radius

    def _replace_ant(self, ant_idx):
        angle = random.uniform(0., np.pi * 2)
        self._pos[ant_idx] = self._get_free_ant_pos()
        self._vel[ant_idx] = np.array([np.cos(angle), np.sin(angle)]) * conf.velocity
        self._kinds[ant_idx] = ant_kind.ant_from_same_category(self._kinds[ant_idx])

    def _get_free_ant_pos(self):
        pos = np.random.rand(2) * conf.field_size
        valid = False
        while not valid:  # randomize until no collision to other points.
            valid = True
            for i in range(conf.ant_amount):
                if not np.isnan(self._pos[i][0]):
                    dist = euclid_dist(self._pos[i] - pos)
                    if dist < 2 * conf.ant_radius:  # collision with an existing ant
                        pos = np.random.rand(2) * conf.field_size
                        valid = False
                        break
        return pos.astype('float64')


@njit
def euclid_dist(vec):
    return (vec[0] ** 2 + vec[1] ** 2) ** .5


@njit
def _collision_calc(pos):
    coll_count = 0
    collisions = np.array([[-1, -1]] * conf.ant_amount)
    already_calculated = [False] * conf.ant_amount

    for i in range(conf.ant_amount):
        for k in range(i + 1, conf.ant_amount):
            if not already_calculated[k]:
                dist = euclid_dist(pos[k] - pos[i])
                if dist < 2 * conf.ant_radius:
                    already_calculated[k] = True
                    collisions[coll_count] = np.array([i, k])
                    coll_count += 1
    return list(collisions)


# call njit compiler
euclid_dist(np.zeros(2))
_collision_calc(np.full((conf.ant_amount, 2), np.nan, dtype='float64'))

