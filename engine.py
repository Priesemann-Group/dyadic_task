import time
import conf as c
import random as r
import numpy as np
from numba import njit

pos = np.full((c.ant_amount, 2), np.nan, dtype='float64')
vel = np.full((c.ant_amount, 2), np.nan, dtype='float64')
rad = np.full(c.ant_amount, np.nan, dtype='float64')

# nan => botch players can occupy the point
# 0   => player 0 owns the point
# 1   => player 1 owns the point
# everything between: shared between the players
shares = np.full(c.ant_amount, np.nan, dtype='float64')
shares[0] = r.random()
shares[1] = r.random()
shares[2] = r.random()


score = [0, 0]


@njit
def euclid_dist(vec):
    return (vec[0] ** 2 + vec[1] ** 2) ** .5


@njit
def gaussian(x, mu=0., sig=c.max_radius*1.5):
    return 1. / (np.sqrt(2. * np.pi) * sig) * np.exp(-np.power((x - mu) / sig, 2.) / 2)


@njit
def accelerations_calc(ant_positions):
    accelerations = np.zeros_like(ant_positions)
    if not np.isnan(np.sum(ant_positions)):
        for i, current_ant in enumerate(ant_positions):
            for other_ant in ant_positions:
                vec = current_ant - other_ant
                dist = euclid_dist(vec)
                acc = vec * gaussian(dist) / dist / gaussian(0.)
                if not np.isnan(np.sum(acc)):
                    accelerations[i] += acc
    return accelerations


@njit
def collision_calc(ants, radians):
    coll_count = 0
    colls = np.array([[-1, -1]] * len(ants))
    already_calculated = [False] * len(ants)  # TODO resize?

    for i in range(len(ants)):
        for k in range(i + 1, len(ants)):
            if not already_calculated[k]:
                dist = euclid_dist(ants[k] - ants[i])
                if dist < radians[i] + radians[k]:
                    already_calculated[k] = True
                    colls[coll_count] = np.array([i, k])
                    coll_count += 1
    return list(colls)


def load():
    global pos, vel, rad
    #collision_calc(pos, rad)
    accelerations_calc(pos)
    euclid_dist(np.array([0, 0]))
    gaussian(0.)
    for _ in range(c.ant_amount):  # TODO
        add_rand_ant()


def add_ant(x, y, angle, radius=None):
    if not radius:  # TODO del this
        radius = r.uniform(c.min_radius, c.max_radius)
    global pos, vel
    i = np.where(np.isnan(pos[:, 0]))[0][0]  # Assumption: There is always at least one nan!
    pos[i] = np.array([x, y], dtype='float64')
    vel[i] = np.array([np.cos(angle), np.sin(angle)]) * c.velocity
    rad[i] = radius


def add_rand_ant():
    x, y = r.randrange(c.field_size[0]), r.randrange(c.field_size[1])
    radius = r.uniform(c.min_radius, c.max_radius)
    proposed_pos = np.array([x, y])
    is_valid = True
    while is_valid:  # randomize until no collision to other points.
        is_valid = False
        for i in range(len(pos)):
            if not np.isnan(pos[i][0]):
                dist = euclid_dist(pos[i] - proposed_pos)
                if dist < rad[i] + radius:
                    x, y = r.randrange(c.field_size[0]), r.randrange(c.field_size[1])
                    radius = r.uniform(c.min_radius, c.max_radius)
                    proposed_pos = np.array([x, y])
                    is_valid = True
                    break
    angle = r.uniform(0., np.pi * 2)
    add_ant(x, y, angle)


def rad_to_area(i):
    return np.pi * rad[i] ** 2


def collision_next_iter(i, k):
    global pos, vel
    return euclid_dist((pos[i] - vel[i]) - (pos[k] - vel[k])) < rad[i] + rad[k]


collided_last_iter = []


def collisions():
    global pos, vel
    colls = collision_calc(pos, rad)
    for i, k in colls:
        if i == -1:
            break
        if tuple(sorted((i, k))) in collided_last_iter:
            if collision_next_iter(i, k):
                continue
            else:
                collided_last_iter.remove(tuple(sorted((i, k))))
        area_i = rad_to_area(i)
        area_k = rad_to_area(k)
        joint_vel = (vel[i] * area_i + vel[k] * area_k) / (area_i + area_k)
        vel[i] = 2 * joint_vel - vel[i]
        vel[k] = 2 * joint_vel - vel[k]
        if collision_next_iter(i, k):
            collided_last_iter.append(tuple(sorted((i, k))))


def correct_to_boundaries():
    for i in range(len(pos)):
        if not np.isnan(pos[i][0]):
            if pos[i][0] < 0 + rad[i]:
                pos[i][0] = 1 + rad[i]
                vel[i][0] *= -1
            elif pos[i][0] > c.field_size[0] - rad[i]:
                pos[i][0] = c.field_size[0] - 1 - rad[i]
                vel[i][0] *= -1
            if pos[i][1] < 0 + rad[i]:
                pos[i][1] = 1 + rad[i]
                vel[i][1] *= -1
            elif pos[i][1] > c.field_size[1] - rad[i]:
                pos[i][1] = c.field_size[1] - 1 - rad[i]
                vel[i][1] *= -1


def update(dt):
    global pos, vel
    acc = accelerations_calc(pos)
    vel += acc
    for v in vel:
        v /= euclid_dist(v)
        v *= c.velocity
    pos += vel
    # collisions()
    correct_to_boundaries()


target_idx = [-1, -1]
target_occupation_date = [0., 0.]


def check_for_target(i, mouse_pos):
    global target_idx, target_occupation_date, pos
    for k, p in enumerate(pos):
        dist = euclid_dist(p - mouse_pos)
        if dist < rad[k]:
            target_idx[i] = k
            target_occupation_date[i] = time.time() + c.time_to_occupy


def occupied(player_idx):
    global target_idx, target_occupation_date, score
    if np.isnan(shares[target_idx[player_idx]]):
        pos[target_idx[player_idx]] = np.array([np.nan, np.nan])  # TODO
        add_rand_ant()

        score[player_idx] += 1

        target_idx[player_idx] = -1
        target_occupation_date[player_idx] = 0.


def get_target_state(mouse_positions):
    global target_idx, target_occupation_date, score
    out = [-1, -1]
    occupations = {}
    for player_idx, mouse_pos in enumerate(mouse_positions):
        mouse_pos = np.array(mouse_pos)
        if target_idx[player_idx] != -1:  # mouse was on a target
            dist = euclid_dist(pos[target_idx[player_idx]] - mouse_pos)
            if dist < rad[target_idx[player_idx]]:  # mouse is still on the target
                t = time.time()
                if t > target_occupation_date[player_idx]:  # occupied the target
                    occupations[player_idx] = target_idx[player_idx]
                else:  # not occupied jet
                    time_left = target_occupation_date[player_idx] - t
                    out[player_idx] = target_idx[player_idx] + time_left / c.time_to_occupy
            else:  # mouse was on a target but lost it
                target_idx[player_idx] = -1
                target_occupation_date[player_idx] = 0.
        else:  # mouse was on no target, check if it is now
            check_for_target(player_idx, mouse_pos)

    if len(occupations) == 2 and occupations[0] == occupations[1]:  # Both players occupied the same target
        if not np.isnan(shares[target_idx[0]]):  # A shared target is occupied
            pos[target_idx[0]] = np.array([np.nan, np.nan])  # TODO
            add_rand_ant()
            score[0] += shares[target_idx[0]]
            score[1] += 1-shares[target_idx[0]]
            for player_idx in [0, 1]:
                target_idx[player_idx] = -1
                target_occupation_date[player_idx] = 0.
        else:  # Edge case: Both players occupied a not shared target at same time (< 1/80s)
            score[0] += .5
            score[1] += .5
    else:  # Consume occupations
        for player_idx in occupations.keys():
            occupied(player_idx)

    return out
